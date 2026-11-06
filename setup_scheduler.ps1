# Registers 3 Windows Scheduled Tasks for Wedding & E-Invitation AI Outreach Engine
# Batches:
# 1. Morning (10:00 AM) - India & South Asia Luxury Wedding Planners
# 2. Afternoon (02:30 PM) - Dubai, UAE & UK Destination Planners
# 3. Night (08:00 PM) - USA, Canada & Global NRI Wedding Planners

$WorkingDir = $PSScriptRoot
$BatchScript = "$WorkingDir\run_batch.bat"

$Batches = @(
    @{ Name = "WeddingOutreach_Morning"; Time = "10:00AM"; Arg = "morning"; Desc = "Morning Batch: India & South Asia Wedding Planners" },
    @{ Name = "WeddingOutreach_Afternoon"; Time = "02:30PM"; Arg = "afternoon"; Desc = "Afternoon Batch: Dubai, UAE & UK Destination Planners" },
    @{ Name = "WeddingOutreach_Night"; Time = "08:00PM"; Arg = "night"; Desc = "Night Batch: USA, Canada & NRI Wedding Planners" }
)

foreach ($b in $Batches) {
    $Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchScript`" $($b.Arg)" -WorkingDirectory $WorkingDir
    $Trigger = New-ScheduledTaskTrigger -Daily -At $b.Time
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances Parallel

    try {
        Unregister-ScheduledTask -TaskName $b.Name -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $b.Name -Action $Action -Trigger $Trigger -Settings $Settings -Description $b.Desc
        Write-Host "Successfully registered '$($b.Name)' to run daily at $($b.Time)" -ForegroundColor Green
    } catch {
        Write-Host "Error registering task '$($b.Name)': $($_.Exception.Message)" -ForegroundColor Red
    }
}
