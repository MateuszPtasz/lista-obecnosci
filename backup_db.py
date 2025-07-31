#!/usr/bin/env python3
# backup_db.py - Database backup and migration utility

import sqlite3
import shutil
import os
import gzip
from datetime import datetime
import argparse
import json
from typing import Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, db_path: str = "shifts.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, compress: bool = True) -> str:
        """Create database backup"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"lista_obecnosci_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Create backup using SQLite backup API
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            logger.info(f"Database backed up to: {backup_path}")
            
            # Compress if requested
            if compress:
                compressed_path = backup_path + ".gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                os.remove(backup_path)
                backup_path = compressed_path
                logger.info(f"Backup compressed to: {backup_path}")
            
            # Create backup metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "original_db": self.db_path,
                "backup_file": backup_path,
                "compressed": compress,
                "size_bytes": os.path.getsize(backup_path)
            }
            
            metadata_path = backup_path.replace('.db', '.json').replace('.gz', '.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            # Cleanup on failure
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def restore_backup(self, backup_path: str, target_db: str = None) -> str:
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file {backup_path} not found")
        
        if target_db is None:
            target_db = self.db_path
        
        try:
            # Handle compressed backups
            if backup_path.endswith('.gz'):
                temp_db = backup_path.replace('.gz', '')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_from = temp_db
            else:
                restore_from = backup_path
            
            # Create backup of current database if it exists
            if os.path.exists(target_db):
                current_backup = f"{target_db}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(target_db, current_backup)
                logger.info(f"Current database backed up to: {current_backup}")
            
            # Restore database
            shutil.copy2(restore_from, target_db)
            
            # Cleanup temp file if it was decompressed
            if backup_path.endswith('.gz') and os.path.exists(temp_db):
                os.remove(temp_db)
            
            logger.info(f"Database restored from: {backup_path} to: {target_db}")
            return target_db
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    def list_backups(self) -> list:
        """List available backups"""
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("lista_obecnosci_backup_") and (filename.endswith('.db') or filename.endswith('.db.gz')):
                backup_path = os.path.join(self.backup_dir, filename)
                metadata_path = backup_path.replace('.db', '.json').replace('.gz', '.json')
                
                backup_info = {
                    "filename": filename,
                    "path": backup_path,
                    "size": os.path.getsize(backup_path),
                    "created": datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat()
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        backup_info.update(metadata)
                    except Exception:
                        pass
                
                backups.append(backup_info)
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """Remove old backup files"""
        backups = self.list_backups()
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        removed_count = 0
        for backup in backups[keep_count:]:  # Keep at least keep_count backups
            backup_date = datetime.fromisoformat(backup['created'].replace('Z', '+00:00').replace('+00:00', ''))
            if backup_date < cutoff_date:
                try:
                    os.remove(backup['path'])
                    # Remove metadata file if it exists
                    metadata_path = backup['path'].replace('.db', '.json').replace('.gz', '.json')
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    logger.info(f"Removed old backup: {backup['filename']}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Failed to remove backup {backup['filename']}: {e}")
        
        logger.info(f"Cleanup complete. Removed {removed_count} old backups.")
        return removed_count

def main():
    parser = argparse.ArgumentParser(description="Database backup utility for Lista Obecności")
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup'], 
                       help='Action to perform')
    parser.add_argument('--db', default='shifts.db', help='Database file path')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--backup-file', help='Backup file for restore operation')
    parser.add_argument('--no-compress', action='store_true', help='Do not compress backup')
    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep backups during cleanup')
    parser.add_argument('--keep-count', type=int, default=10, help='Minimum number of backups to keep')
    
    args = parser.parse_args()
    
    backup_manager = DatabaseBackup(args.db, args.backup_dir)
    
    try:
        if args.action == 'backup':
            backup_path = backup_manager.create_backup(compress=not args.no_compress)
            print(f"Backup created: {backup_path}")
            
        elif args.action == 'restore':
            if not args.backup_file:
                print("Error: --backup-file required for restore operation")
                return 1
            restored_db = backup_manager.restore_backup(args.backup_file)
            print(f"Database restored to: {restored_db}")
            
        elif args.action == 'list':
            backups = backup_manager.list_backups()
            if not backups:
                print("No backups found")
            else:
                print(f"Found {len(backups)} backups:")
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    print(f"  {backup['filename']} ({size_mb:.1f} MB) - {backup['created']}")
                    
        elif args.action == 'cleanup':
            removed = backup_manager.cleanup_old_backups(args.keep_days, args.keep_count)
            print(f"Removed {removed} old backups")
            
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())