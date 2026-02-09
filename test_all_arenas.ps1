#!/usr/bin/env pwsh
# Test automatique Équipe 6 - Toutes les arènes (0-9)

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🏆 TEST ÉQUIPE 6 - TOUTES LES ARÈNES (0-9)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$arenas = @(
    @{id=0; name="Empty (TRÈS FACILE)"},
    @{id=1; name="Classic (FACILE)"},
    @{id=2; name="Lines (MOYEN)"},
    @{id=3; name="Vertical Limit (MOYEN)"},
    @{id=4; name="Maze (DIFFICILE)"},
    @{id=5; name="Challenge 1 (AVANCÉ)"},
    @{id=6; name="Challenge 2 (AVANCÉ)"},
    @{id=7; name="Challenge 3 (AVANCÉ)"},
    @{id=8; name="Challenge 4 (AVANCÉ)"},
    @{id=9; name="Challenge 5 (TRÈS DIFFICILE)"}
)

$results = @()
$start_time = Get-Date

foreach ($arena in $arenas) {
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Yellow
    Write-Host "🎮 Arène $($arena.id): $($arena.name)" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor Yellow
    
    $arena_start = Get-Date
    
    # Lancer le test
    python .\tetracomposibot.py config_Paintwars $($arena.id) False
    
    $arena_end = Get-Date
    $duration = ($arena_end - $arena_start).TotalSeconds
    
    Write-Host "✅ Arène $($arena.id) terminée en $([Math]::Round($duration, 2))s" -ForegroundColor Green
    Write-Host ""
    
    $results += @{
        arena = $arena.id
        name = $arena.name
        duration = $duration
    }
}

$end_time = Get-Date
$total_duration = ($end_time - $start_time).TotalSeconds

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 RÉSULTATS FINAUX" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Arènes testées:" -ForegroundColor White
foreach ($result in $results) {
    Write-Host "  ✓ Arène $($result.arena) - $($result.name): $([Math]::Round($result.duration, 2))s" -ForegroundColor Green
}

Write-Host ""
Write-Host "Temps total: $([Math]::Round($total_duration, 2))s" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ TOUS LES TESTS TERMINÉS!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
