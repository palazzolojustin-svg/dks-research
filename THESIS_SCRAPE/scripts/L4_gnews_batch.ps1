# L4: batch of Google News article pulls (rerun: powershell -File L4_gnews_batch.ps1)
$kw = "million|savings|basis points|bps|hours|positions|roles|store manager|assistant|layer|eliminat|payroll|labor"
$q = @(
 @("Barnes & Noble job cuts labor model 40 million savings 2018", "Barnes"),
 @("Best Buy lays off 5,000 store workers 2021 labor model", "Best Buy"),
 @("Best Buy cuts store jobs 2022", "Best Buy"),
 @("Target cuts 500 jobs invests store staffing 2026", "Target"),
 @("Target store team structure change 2019 specialists", "Target"),
 @("Lowe's eliminates assistant store manager positions", "Lowe"),
 @("Lowe's restructuring store staffing 2018 jobs", "Lowe"),
 @("Home Depot store labor model change hours", "Home Depot"),
 @("Kohl's store payroll reduction labor", "Kohl"),
 @("Gap layoffs 1,800 store leadership 2023", "Gap"),
 @("Bed Bath Beyond store managers layoffs 2019 restructuring", "Bed Bath"),
 @("Michaels eliminates store manager positions", "Michaels"),
 @("Petco store labor model savings", "Petco"),
 @("Big Lots store labor savings Operation North Star", "Big Lots"),
 @("Foot Locker store labor model cost savings", "Foot Locker"),
 @("Academy Sports self-checkout labor savings", "Academy"),
 @("Ulta Beauty store labor model", "Ulta"),
 @("Dollar General store labor hours investment back to basics", "Dollar General"),
 @("Bath & Body Works store labor savings profit optimization", "Bath"),
 @("JCPenney store restructuring eliminates positions savings", "Penney"),
 @("Macy's store management restructuring layers eliminated", "Macy"),
 @("Walgreens store manager restructuring savings", "Walgreens"),
 @("Rite Aid store labor model", "Rite Aid"),
 @("Kroger store labor savings", "Kroger"),
 @("Walmart eliminates store positions team lead 2019 restructuring", "Walmart"),
 @("Sam's Club store management restructuring", "Sam")
)
foreach ($p in $q) {
  python C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\scripts\L4_gnews_fetch.py $p[0] $p[1] $kw 3 2>$null
  Start-Sleep 4
}
