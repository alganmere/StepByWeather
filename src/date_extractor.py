import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import csv
import os

def extract_step_data(xml_file):
    # Read the file content
    with open(xml_file, 'r') as f:
        content = f.readlines()
    
    # Remove the XML declaration line
    filtered_content = [line for line in content if not line.strip().startswith('<?')]
    xml_content = ''.join(filtered_content)
    
    try:
        root = ET.fromstring(xml_content)
        step_data = []
        
        # Look for all Record elements with step count type
        for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierStepCount']"):
            try:
                start_date = datetime.strptime(record.get('startDate'), "%Y-%m-%d %H:%M:%S %z")
                end_date = datetime.strptime(record.get('endDate'), "%Y-%m-%d %H:%M:%S %z")
                steps = int(record.get('value'))
                source = record.get('sourceName')
                
                # Calculate duration in minutes
                duration = (end_date - start_date).total_seconds() / 60
                
                step_data.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'steps': steps,
                    'duration_minutes': round(duration, 2),
                    'steps_per_minute': round(steps / duration, 2) if duration > 0 else 0,
                    'source': source
                })
                
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error processing record: {e}")
                continue
        
        return step_data
    
    except ET.ParseError as e:
        print(f"XML Parsing Error: {str(e)}")
        return None

def save_to_csv(step_data, output_file):
    # Define CSV headers
    headers = [
        'start_date',
        'end_date',
        'steps',
        'duration_minutes',
        'steps_per_minute',
        'source'
    ]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        # Sort data by start_date before writing
        sorted_data = sorted(step_data, key=lambda x: x['start_date'])
        
        for record in sorted_data:
            # Format datetime objects to strings
            record['start_date'] = record['start_date'].strftime('%Y-%m-%d %H:%M:%S %z')
            record['end_date'] = record['end_date'].strftime('%Y-%m-%d %H:%M:%S %z')
            writer.writerow(record)

def main():
    xml_file = "export.xml"
    output_file = "data/step_data.csv"
    
    try:
        print("Extracting step data from XML...")
        step_data = extract_step_data(xml_file)
        
        if step_data:
            # Get date range
            start_dates = [record['start_date'] for record in step_data]
            end_dates = [record['end_date'] for record in step_data]
            earliest_date = min(start_dates)
            latest_date = max(end_dates)
            
            print(f"\nDate Range for Step Count Data:")
            print(f"Earliest: {earliest_date.strftime('%Y-%m-%d %H:%M:%S %z')}")
            print(f"Latest: {latest_date.strftime('%Y-%m-%d %H:%M:%S %z')}")
            
            # Save to CSV
            print(f"\nSaving data to {output_file}...")
            save_to_csv(step_data, output_file)
            print(f"Successfully saved {len(step_data)} records!")
            
            # Print some basic stats
            total_steps = sum(record['steps'] for record in step_data)
            print(f"\nTotal steps recorded: {total_steps:,}")
            
        else:
            print("No valid step count data found in the XML file")
            
    except FileNotFoundError:
        print(f"Error: Could not find the XML file at '{xml_file}'")
        print("Make sure the XML file is in the correct location")
    except Exception as e:
        print(f"Error processing the XML file: {str(e)}")

if __name__ == "__main__":
    main() 