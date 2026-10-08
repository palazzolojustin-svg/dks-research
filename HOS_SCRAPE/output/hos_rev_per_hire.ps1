# House of Sport: revenue per added job. Run:  powershell -ExecutionPolicy Bypass -File .\hos_rev_per_hire.ps1
$f = "{0,-31} {1,-52} {2,10} {3,9} {4,13}"
$rows = @(
  @('Item','Source','SalesAdded','JobsAdded','RevPerHosHire'),
  @('----','------','----------','---------','-------------'),
  @('Victor, Eastview Mall','NY Sales Tax (Ontario Co.), BLS Jobs (Ontario Co.)','$28.1M','128','$219K'),
  @('Clifton Park, Bass Pro Shops','NY Sales Tax (Saratoga Co.), BLS Jobs (Saratoga Co.)','$31.1M','148','$210K'),
  @('Tampa, International Plaza Mall','Mall Loan (BBCMS 2025-5C38), BLS Jobs (Hillsborough)','$24.0M','123','$195K'),
  @('Sioux Falls, Empire Mall','Mall Loan (WFCM 2026-5C8), Staffing Benchmark','$12.2M','57','$214K'),
  @('Minnetonka, Ridgedale Center','Mall Loan (BMO/BBCMS 424H), BLS Jobs (Hennepin Co.)','$31.2M','151','$207K'),
  @('AVERAGE','','','','$209K')
)
Write-Output ''
foreach ($r in $rows) { Write-Output ($f -f $r[0],$r[1],$r[2],$r[3],$r[4]) }
Write-Output ''
