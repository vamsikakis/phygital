#!/usr/bin/env python3
"""
Populate Community Drive with Sample Documents
Creates sample documents for testing the community drive functionality
"""

import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Flask app for context
from app import app

def create_sample_document(filename: str, content: str, category: str = 'general') -> str:
    """Create a sample document file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{filename}', delete=False, encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def populate_sample_documents():
    """Create and store sample documents in the community drive"""

    # Import inside function to avoid circular imports
    from services.community_drive_service import community_drive_service
    
    sample_documents = [
        {
            'filename': 'Gopalan_Atlantis_Bylaws_2024.txt',
            'category': 'bylaws',
            'content': """
GOPALAN ATLANTIS OWNERS ASSOCIATION
BYLAWS - 2024 EDITION

ARTICLE I - NAME AND PURPOSE
The name of this association shall be "Gopalan Atlantis Owners Association" (GAAOA).

ARTICLE II - DEFINITIONS
1. "Association" means Gopalan Atlantis Owners Association
2. "Owner" means the record owner of a unit
3. "Unit" means an individual apartment or commercial space

ARTICLE III - MEMBERSHIP
Every owner of a unit shall be a member of the Association.

ARTICLE IV - MEETINGS
1. Annual meetings shall be held in March of each year
2. Special meetings may be called by the Board or by 25% of members
3. Quorum shall be 30% of total membership

ARTICLE V - BOARD OF DIRECTORS
1. The Board shall consist of 7 members
2. Directors serve 2-year terms
3. The Board shall meet monthly

ARTICLE VI - ASSESSMENTS
1. Monthly maintenance fees are due by the 5th of each month
2. Late fees apply after the 10th of the month
3. Special assessments require 75% approval

This document was last updated on: """ + datetime.now().strftime('%Y-%m-%d')
        },
        {
            'filename': 'Community_Rules_and_Regulations.txt',
            'category': 'general',
            'content': """
GOPALAN ATLANTIS COMMUNITY RULES

NOISE POLICY
- Quiet hours: 10 PM to 6 AM daily
- No loud music or construction during quiet hours
- Complaints should be reported to security

PARKING REGULATIONS
- Each unit has assigned parking slots
- Visitor parking limited to 24 hours
- No commercial vehicles overnight
- Towing enforced for violations

PET POLICY
- Maximum 2 pets per unit
- Dogs must be leashed in common areas
- Pet waste must be cleaned immediately
- Registration required with management

COMMON AREA USAGE
- Swimming pool hours: 6 AM to 10 PM
- Gym access 24/7 with key card
- Community hall booking required
- Children under 12 must be supervised

WASTE MANAGEMENT
- Segregate wet and dry waste
- Collection times: 7 AM and 7 PM
- No dumping in common areas
- Composting encouraged

Updated: """ + datetime.now().strftime('%Y-%m-%d')
        },
        {
            'filename': 'Emergency_Procedures_Guide.txt',
            'category': 'security',
            'content': """
EMERGENCY PROCEDURES - GOPALAN ATLANTIS

FIRE EMERGENCY
1. Sound alarm immediately
2. Evacuate via nearest stairwell
3. Do not use elevators
4. Assembly point: Main gate area
5. Call Fire Department: 101

MEDICAL EMERGENCY
1. Call ambulance: 108
2. Notify security: 080-XXXX-XXXX
3. Provide first aid if trained
4. Clear path for emergency vehicles

SECURITY THREATS
1. Contact security immediately
2. Do not confront intruders
3. Lock doors and stay inside
4. Call police: 100

POWER OUTAGE
1. Check main electrical panel
2. Report to maintenance
3. Use emergency lighting
4. Avoid using candles

WATER EMERGENCY
1. Shut off main water valve if needed
2. Report to maintenance immediately
3. Document any damage
4. Contact insurance if required

ELEVATOR EMERGENCY
1. Press emergency button
2. Call security
3. Do not attempt to exit on your own
4. Wait for professional help

CONTACT NUMBERS
Security: 080-XXXX-XXXX
Maintenance: 080-YYYY-YYYY
Management: 080-ZZZZ-ZZZZ
Police: 100
Fire: 101
Ambulance: 108

Last updated: """ + datetime.now().strftime('%Y-%m-%d')
        },
        {
            'filename': 'Amenities_Usage_Guide.txt',
            'category': 'facilities',
            'content': """
AMENITIES USAGE GUIDE - GOPALAN ATLANTIS

SWIMMING POOL
- Hours: 6:00 AM to 10:00 PM
- Children under 12 must be accompanied
- No diving allowed
- Pool cleaning: Mondays 6-8 AM
- Maximum capacity: 25 people

GYMNASIUM
- 24/7 access with key card
- Age limit: 16 years and above
- Bring your own towel
- Equipment training available
- Report any damage immediately

COMMUNITY HALL
- Advance booking required (48 hours)
- Capacity: 100 people
- Rental fee: ₹2,000 per day
- Cleaning deposit: ₹1,000
- No alcohol without permission

CHILDREN'S PLAY AREA
- Hours: 6:00 AM to 8:00 PM
- Children under 10 only
- Adult supervision required
- No food or drinks allowed
- Report any damage

JOGGING TRACK
- Open 24/7
- Clockwise direction only
- No cycling allowed
- Keep right while walking
- Emergency phones available

TENNIS COURT
- Booking required
- Hours: 6:00 AM to 10:00 PM
- Maximum 2 hours per booking
- Bring your own equipment
- Court fee: ₹200 per hour

LIBRARY
- Hours: 9:00 AM to 9:00 PM
- Silence must be maintained
- Books can be borrowed for 2 weeks
- Late return fine: ₹10 per day
- No food or drinks

Updated: """ + datetime.now().strftime('%Y-%m-%d')
        },
        {
            'filename': 'Maintenance_Request_Procedures.txt',
            'category': 'general',
            'content': """
MAINTENANCE REQUEST PROCEDURES

HOW TO SUBMIT REQUESTS
1. Online: Use the facility management app
2. Phone: Call maintenance hotline
3. Email: maintenance@gopalanatlantis.com
4. In-person: Visit management office

EMERGENCY REQUESTS (24/7)
- Water leaks
- Electrical failures
- Elevator breakdowns
- Security issues
- Gas leaks

Response time: Within 2 hours

ROUTINE REQUESTS
- Plumbing repairs
- Electrical work
- Painting
- Appliance repairs
- General maintenance

Response time: Within 48 hours

SCHEDULED MAINTENANCE
- AC servicing: Quarterly
- Elevator maintenance: Monthly
- Generator testing: Weekly
- Fire safety checks: Monthly
- Pest control: Bi-monthly

RESIDENT RESPONSIBILITIES
- Provide access to units
- Report issues promptly
- Maintain unit interiors
- Follow safety guidelines
- Pay for damages caused by negligence

CONTACT INFORMATION
Maintenance Hotline: 080-XXXX-XXXX
Email: maintenance@gopalanatlantis.com
Office Hours: 9 AM to 6 PM
Emergency: 24/7 available

Last updated: """ + datetime.now().strftime('%Y-%m-%d')
        }
    ]
    
    print("🏗️ Populating Community Drive with Sample Documents")
    print("=" * 60)
    
    created_count = 0
    
    for doc_info in sample_documents:
        try:
            # Create temporary file
            temp_path = create_sample_document(
                doc_info['filename'],
                doc_info['content'],
                doc_info['category']
            )
            
            # Store in community drive
            community_drive_service.store_document(
                file_path=temp_path,
                original_filename=doc_info['filename'],
                category=doc_info['category'],
                description=f"Sample {doc_info['category']} document for Gopalan Atlantis community"
            )
            
            print(f"✅ Created: {doc_info['filename']} ({doc_info['category']})")
            created_count += 1
            
            # Clean up temp file
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"❌ Failed to create {doc_info['filename']}: {e}")
    
    print(f"\n🎉 Successfully created {created_count} sample documents!")
    
    # Show storage stats
    stats = community_drive_service.get_storage_stats()
    print(f"\nStorage Statistics:")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total size: {stats['total_size']} bytes")
    print(f"Categories: {list(stats['categories'].keys())}")

if __name__ == "__main__":
    with app.app_context():
        populate_sample_documents()
