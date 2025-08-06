#!/usr/bin/env python3
"""
LXCloud Data Cleanup Script
Cleans up old data records based on year retention policy
"""

import pymysql
import argparse
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'lxcloud',
    'password': 'lxcloud123',
    'database': 'lxcloud',
    'charset': 'utf8mb4'
}

def cleanup_old_data(years_to_keep=1, dry_run=False):
    """
    Clean up screen data older than specified years
    
    Args:
        years_to_keep (int): Number of years of data to keep
        dry_run (bool): If True, only show what would be deleted
    """
    current_year = datetime.now().year
    cutoff_year = current_year - years_to_keep
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Count records to be deleted
        cursor.execute("""
            SELECT COUNT(*) FROM screen_data 
            WHERE year < %s
        """, (cutoff_year,))
        
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("No old data found to clean up.")
            return
        
        logger.info(f"Found {count} records from before {cutoff_year} to clean up.")
        
        if dry_run:
            logger.info("DRY RUN: Would delete these records but not actually deleting.")
            
            # Show breakdown by year
            cursor.execute("""
                SELECT year, COUNT(*) as count 
                FROM screen_data 
                WHERE year < %s 
                GROUP BY year 
                ORDER BY year
            """, (cutoff_year,))
            
            for year, year_count in cursor.fetchall():
                logger.info(f"  Year {year}: {year_count} records")
        else:
            # Actually delete the records
            cursor.execute("""
                DELETE FROM screen_data 
                WHERE year < %s
            """, (cutoff_year,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            logger.info(f"Successfully deleted {deleted_count} old data records.")
            
            # Optimize table after deletion
            cursor.execute("OPTIMIZE TABLE screen_data")
            logger.info("Table optimization completed.")
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def cleanup_offline_screens(days_offline=30, dry_run=False):
    """
    Mark screens as offline if they haven't been seen for specified days
    
    Args:
        days_offline (int): Number of days to consider a screen offline
        dry_run (bool): If True, only show what would be updated
    """
    cutoff_date = datetime.now() - timedelta(days=days_offline)
    
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Find screens that should be marked offline
        cursor.execute("""
            SELECT id, serial_number, custom_name, last_seen
            FROM screens 
            WHERE online_status = TRUE AND last_seen < %s
        """, (cutoff_date,))
        
        screens_to_update = cursor.fetchall()
        
        if not screens_to_update:
            logger.info("No screens need to be marked offline.")
            return
        
        logger.info(f"Found {len(screens_to_update)} screens to mark offline:")
        
        for screen_id, serial, name, last_seen in screens_to_update:
            display_name = name if name else serial
            logger.info(f"  {display_name} (Serial: {serial}) - Last seen: {last_seen}")
        
        if dry_run:
            logger.info("DRY RUN: Would mark these screens offline but not actually updating.")
        else:
            # Update screens to offline status
            cursor.execute("""
                UPDATE screens 
                SET online_status = FALSE 
                WHERE online_status = TRUE AND last_seen < %s
            """, (cutoff_date,))
            
            updated_count = cursor.rowcount
            conn.commit()
            logger.info(f"Successfully marked {updated_count} screens as offline.")
    
    except Exception as e:
        logger.error(f"Error during screen status cleanup: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='LXCloud Data Cleanup Script')
    parser.add_argument('--years', type=int, default=1, 
                      help='Number of years of data to keep (default: 1)')
    parser.add_argument('--offline-days', type=int, default=30,
                      help='Mark screens offline after this many days (default: 30)')
    parser.add_argument('--dry-run', action='store_true',
                      help='Show what would be cleaned but don\'t actually delete')
    parser.add_argument('--data-only', action='store_true',
                      help='Only clean up data records, not screen status')
    parser.add_argument('--screens-only', action='store_true',
                      help='Only update screen status, not data records')
    
    args = parser.parse_args()
    
    logger.info("Starting LXCloud data cleanup...")
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no actual changes will be made")
    
    try:
        if not args.screens_only:
            logger.info("=== Data Records Cleanup ===")
            cleanup_old_data(args.years, args.dry_run)
        
        if not args.data_only:
            logger.info("=== Screen Status Cleanup ===")
            cleanup_offline_screens(args.offline_days, args.dry_run)
        
        logger.info("Cleanup completed successfully.")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())