# Staggered Research Cron Setup
# Run this to create all research cron jobs with 2-hour spacing

$jobs = @(
    @{ Name="research-self-improvement"; Time="0 7 * * *"; Trigger="TRIGGER-RESEARCH-self-improvement"; },
    @{ Name="research-openclaw-system"; Time="0 9 * * *"; Trigger="TRIGGER-RESEARCH-OpenClaw-AI"; },
    @{ Name="research-kdp-income"; Time="0 11 * * *"; Trigger="TRIGGER-RESEARCH-kdp-coloring-books"; },
    @{ Name="research-ai-tools"; Time="0 13 * * *"; Trigger="TRIGGER-RESEARCH-ai-tools"; },
    @{ Name="research-local-llm"; Time="0 15 * * *"; Trigger="TRIGGER-RESEARCH-local-llm"; },
    @{ Name="research-security"; Time="0 17 * * *"; Trigger="TRIGGER-RESEARCH-security"; },
    @{ Name="research-emerging-tech"; Time="0 19 * * *"; Trigger="TRIGGER-RESEARCH-emerging-tech"; },
    @{ Name="research-philosophy"; Time="0 21 * * *"; Trigger="TRIGGER-RESEARCH-philosophy"; }
)

foreach ($job in $jobs) {
    Write-Host "Creating cron job: $($job.Name) at $($job.Time)"
    openclaw cron create `n        --name $job.Name `n        --schedule $job.Time `n        --timezone "Europe/Dublin" `n        --target main `n        --payload "systemEvent:$($job.Trigger)"
}

Write-Host "`nAll research cron jobs created!"
Write-Host "Schedule: Every 2 hours from 7 AM to 9 PM"
