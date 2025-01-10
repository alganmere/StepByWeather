import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import calendar
import numpy as np

def load_and_prepare_data():
    """Load and prepare both step and weather data"""
    # Load datasets
    steps_df = pd.read_csv('data/step_data.csv')
    weather_df = pd.read_csv('data/weather_data.csv')
    
    # Convert dates to datetime
    steps_df['start_date'] = pd.to_datetime(steps_df['start_date'])
    weather_df['time'] = pd.to_datetime(weather_df['time'])
    
    # Create date-only column for merging
    steps_df['date'] = steps_df['start_date'].dt.date
    
    # Add day of week
    steps_df['day_of_week'] = steps_df['start_date'].dt.day_name()
    steps_df['month'] = steps_df['start_date'].dt.month_name()
    steps_df['hour'] = steps_df['start_date'].dt.hour
    
    # Aggregate steps by date
    daily_steps = steps_df.groupby('date').agg({
        'steps': 'sum',
        'duration_minutes': 'sum',
        'steps_per_minute': 'mean',
        'day_of_week': 'first',
        'month': 'first'
    }).reset_index()
    
    # Convert date to datetime for merging
    daily_steps['date'] = pd.to_datetime(daily_steps['date'])
    
    # Merge with weather data
    merged_df = pd.merge(
        daily_steps,
        weather_df,
        left_on='date',
        right_on='time',
        how='inner'
    )
    
    return merged_df, steps_df

def create_visualizations(df, hourly_df):
    """Create 10 different visualizations"""
    os.makedirs('output/plots', exist_ok=True)
    
    # 1. Temperature vs Steps with Trend Line
    plt.figure(figsize=(12, 6))
    sns.regplot(data=df, x='temp_mean', y='steps', scatter_kws={'alpha':0.5})
    plt.title('Temperature vs Daily Steps with Trend Line')
    plt.xlabel('Average Temperature (°C)')
    plt.ylabel('Daily Steps')
    plt.savefig('output/plots/1_temperature_steps_trend.png')
    plt.close()
    
    # 2. Steps by Day of Week
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='day_of_week', y='steps', 
                order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                       'Friday', 'Saturday', 'Sunday'])
    plt.title('Step Distribution by Day of Week')
    plt.xticks(rotation=45)
    plt.savefig('output/plots/2_steps_by_day.png')
    plt.close()
    
    # 3. Monthly Step Patterns
    monthly_avg = df.groupby('month')['steps'].mean().reindex(
        calendar.month_name[1:13])
    plt.figure(figsize=(12, 6))
    monthly_avg.plot(kind='bar')
    plt.title('Average Daily Steps by Month')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/plots/3_monthly_patterns.png')
    plt.close()
    
    # 4. Weather Correlation Matrix
    weather_cols = ['steps', 'temp_mean', 'precipitation', 'wind_speed', 
                    'pressure', 'temp_min', 'temp_max']
    plt.figure(figsize=(12, 10))
    sns.heatmap(df[weather_cols].corr(), annot=True, cmap='coolwarm', center=0)
    plt.title('Weather Factors Correlation Matrix')
    plt.tight_layout()
    plt.savefig('output/plots/4_correlation_matrix.png')
    plt.close()
    
    # 5. Steps Distribution by Weather Conditions
    df['weather_condition'] = pd.cut(df['precipitation'],
                                   bins=[-np.inf, 0, 1, np.inf],
                                   labels=['Clear', 'Light Rain', 'Heavy Rain'])
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=df, x='weather_condition', y='steps')
    plt.title('Step Distribution by Weather Condition')
    plt.savefig('output/plots/5_weather_condition_steps.png')
    plt.close()
    
    # 6. Hourly Step Patterns
    hourly_steps = hourly_df.groupby('hour')['steps'].mean()
    plt.figure(figsize=(12, 6))
    hourly_steps.plot(kind='line', marker='o')
    plt.title('Average Steps by Hour of Day')
    plt.xlabel('Hour')
    plt.ylabel('Average Steps')
    plt.grid(True)
    plt.savefig('output/plots/6_hourly_patterns.png')
    plt.close()
    
    # 7. Wind Speed vs Steps with Temperature
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(df['wind_speed'], df['steps'], 
                         c=df['temp_mean'], cmap='viridis')
    plt.colorbar(scatter, label='Temperature (°C)')
    plt.title('Wind Speed vs Steps (Colored by Temperature)')
    plt.xlabel('Wind Speed')
    plt.ylabel('Steps')
    plt.savefig('output/plots/7_wind_temp_steps.png')
    plt.close()
    
    # 8. Monthly Step Trends Over Years
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    yearly_monthly = df.groupby(['year', 'month_num'])['steps'].mean().unstack()
    plt.figure(figsize=(15, 8))
    sns.heatmap(yearly_monthly, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Average Daily Steps by Month and Year')
    plt.savefig('output/plots/8_yearly_monthly_heatmap.png')
    plt.close()
    
    # 9. Step Consistency (Rolling Average)
    df_sorted = df.sort_values('date')
    df_sorted['rolling_avg'] = df_sorted['steps'].rolling(window=30).mean()
    plt.figure(figsize=(15, 6))
    plt.plot(df_sorted['date'], df_sorted['steps'], alpha=0.3, label='Daily Steps')
    plt.plot(df_sorted['date'], df_sorted['rolling_avg'], 
             color='red', label='30-day Average')
    plt.title('Daily Steps with 30-day Moving Average')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/plots/9_step_consistency.png')
    plt.close()
    
    # 10. Temperature Range Impact
    df['temp_range'] = pd.cut(df['temp_mean'], 
                             bins=[-float('inf'), 5, 15, 25, float('inf')],
                             labels=['Cold (<5°C)', 'Mild (5-15°C)', 
                                   'Warm (15-25°C)', 'Hot (>25°C)'])
    temp_day_stats = df.groupby(['temp_range', 'day_of_week'])['steps'].mean().unstack()
    plt.figure(figsize=(12, 8))
    sns.heatmap(temp_day_stats, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Average Steps by Temperature Range and Day of Week')
    plt.tight_layout()
    plt.savefig('output/plots/10_temp_day_heatmap.png')
    plt.close()
    
    return df

def generate_detailed_insights(df):
    """Generate comprehensive insights from the analysis"""
    insights = []
    
    # Overall Statistics
    insights.append("=== WALKING PATTERNS ANALYSIS ===\n")
    
    # 1. Overall Statistics
    insights.append("1. OVERALL STATISTICS")
    insights.append(f"Total days analyzed: {len(df):,}")
    insights.append(f"Average daily steps: {df['steps'].mean():,.0f}")
    insights.append(f"Highest step count: {df['steps'].max():,} steps")
    insights.append(f"Lowest step count: {df['steps'].min():,} steps")
    
    # 2. Temperature Impact
    insights.append("\n2. TEMPERATURE IMPACT")
    temp_stats = df.groupby('temp_range')['steps'].agg(['mean', 'count']).round(2)
    insights.append("Average steps by temperature range:")
    insights.append(str(temp_stats))
    
    # 3. Day of Week Analysis
    insights.append("\n3. DAY OF WEEK PATTERNS")
    day_stats = df.groupby('day_of_week')['steps'].mean().sort_values(ascending=False)
    insights.append("Average steps by day of week:")
    for day, steps in day_stats.items():
        insights.append(f"{day}: {steps:,.0f} steps")
    
    # 4. Weather Impact
    insights.append("\n4. WEATHER IMPACT")
    weather_stats = df.groupby('weather_condition')['steps'].mean().sort_values(ascending=False)
    insights.append("Average steps by weather condition:")
    for condition, steps in weather_stats.items():
        insights.append(f"{condition}: {steps:,.0f} steps")
    
    # 5. Top Walking Days
    insights.append("\n5. TOP WALKING DAYS")
    top_days = df.nlargest(5, 'steps')[['date', 'steps', 'temp_mean', 'weather_condition']]
    insights.append("Top 5 days with highest step counts:")
    for _, row in top_days.iterrows():
        insights.append(f"Date: {row['date'].strftime('%Y-%m-%d')}, "
                       f"Steps: {row['steps']:,}, "
                       f"Temperature: {row['temp_mean']:.1f}°C, "
                       f"Weather: {row['weather_condition']}")
    
    # 6. Seasonal Patterns
    insights.append("\n6. SEASONAL PATTERNS")
    monthly_avg = df.groupby('month')['steps'].mean().sort_values(ascending=False)
    insights.append("Average steps by month:")
    for month, steps in monthly_avg.items():
        insights.append(f"{month}: {steps:,.0f} steps")
    
    # 7. Weather Correlations
    insights.append("\n7. WEATHER CORRELATIONS")
    weather_corr = df[['steps', 'temp_mean', 'precipitation', 
                       'wind_speed', 'pressure']].corr()['steps'].drop('steps')
    insights.append("Correlation with steps:")
    for col, corr in weather_corr.items():
        insights.append(f"{col}: {corr:.3f}")
    
    # 8. Key Findings and Recommendations
    insights.append("\n8. KEY FINDINGS AND RECOMMENDATIONS")
    insights.append("- Best conditions for walking:")
    insights.append(f"  Temperature range: {temp_stats['mean'].idxmax()}")
    insights.append(f"  Day of week: {day_stats.index[0]}")
    insights.append(f"  Weather: {weather_stats.index[0]}")
    
    # Save insights to file
    with open('output/detailed_insights.txt', 'w') as f:
        f.write('\n'.join(insights))
    
    return insights

def main():
    print("Loading and preparing data...")
    merged_df, hourly_df = load_and_prepare_data()
    
    print("Creating visualizations...")
    analyzed_df = create_visualizations(merged_df, hourly_df)
    
    print("Generating detailed insights...")
    insights = generate_detailed_insights(analyzed_df)
    
    print("\nAnalysis complete! Check the output directory for results.")
    print("\nKey insights have been saved to output/detailed_insights.txt")

if __name__ == "__main__":
    main() 