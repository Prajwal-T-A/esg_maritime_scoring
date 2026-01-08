# Raw Data Directory

This directory contains the raw input data for the ML pipeline.

## Required Files

1. **ais_raw.csv** - AIS (Automatic Identification System) maritime data from NOAA
   - Size: ~724 MB
   - Source: NOAA Maritime Data
   - Columns: mmsi, base_date_time, longitude, latitude, sog, cog, heading, vessel_type, length, width, draft, cargo, status, imo

2. **emission_factors.csv** - IMO/IPCC emission factors by vessel type
   - Size: Small (~KB)
   - Source: IMO/IPCC Guidelines
   - Columns: vessel_type, fuel_type, co2_factor

## Data Storage

⚠️ **These files are NOT stored in git** due to their large size (exceeds GitHub's 100 MB limit).

### Options for Data Management

**Option 1: Cloud Storage (Recommended for Production)**
- Store in AWS S3, Google Cloud Storage, or Azure Blob Storage
- Update `ml/config.py` to download from cloud if not present locally
- Use environment variables for cloud credentials

**Option 2: External Download**
- Host on file sharing service (Dropbox, Google Drive, etc.)
- Team members download manually before running pipeline
- Add download script to `setup_and_run.sh`

**Option 3: Git LFS (for smaller datasets)**
- Install Git Large File Storage: `git lfs install`
- Track large files: `git lfs track "ml/data/raw/*.csv"`
- Note: GitHub LFS has bandwidth and storage limits

**Option 4: Local Development Only**
- Keep files locally in this directory
- Each developer maintains their own copy
- Document data source and version in team docs

## Setup Instructions

Before running the ML pipeline, ensure:
1. Place `ais_raw.csv` in this directory
2. Place `emission_factors.csv` in this directory
3. Verify file integrity (optional): check file sizes and row counts

## Data Versioning

For reproducibility, document your data version:
- **AIS Data Version:** [Add version/date here]
- **Emission Factors Version:** [Add version/date here]
- **Last Updated:** [Add date here]

## Security Note

If data contains sensitive information:
- ✅ Ensure files are in .gitignore
- ✅ Never commit to public repositories
- ✅ Use proper access controls
- ✅ Comply with data privacy regulations
