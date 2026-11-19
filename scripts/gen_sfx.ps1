$py = "D:\projects\agentic team for editing\.venv\Scripts\python.exe"
Set-Location "D:\projects\higgsfield test01"
$sfx = @(
  @("clang_heavy_b", "Heavy steel pipe dropped onto a stack of steel pipes, one deep metallic clang with long ringing resonance, outdoor industrial yard, no whoosh, no air swoosh", 2.5),
  @("ring_light", "A single light tap of a metal mallet on a hollow steel pipe, clean bright metallic ping that rings and decays, close and dry, no whoosh", 1.5),
  @("pipes_clatter", "A bundle of steel pipes rolling and clattering into place on a steel rack, metallic rattling that settles into a stack, no whoosh", 3),
  @("odometer", "Heavy mechanical counter rolling fast, rapid precise metal ratchet clicks speeding up then stopping with one final click", 1.5),
  @("scanner", "Industrial x-ray scanner beam sweeping, low electrical hum with a soft rising buzz and faint digital crackle, no whoosh", 2.5),
  @("sub_hit", "Deep cinematic sub bass impact, short low boom with a slight metallic tail, no whoosh, no riser", 2),
  @("pipe_scrape", "Long steel pipe sliding slowly across another steel pipe, continuous metallic scrape with resonance", 3),
  @("hatch_thud", "Massive steel hatch closing, deep resonant metallic thud with a short reverberant ring, cinematic, no whoosh", 2.5),
  @("iris", "Mechanical metal iris shutter closing, quick precise metallic blades sliding and locking with a click", 1)
)
foreach ($s in $sfx) { & $py -I scripts\elevenlabs.py sfx $s[0] $s[1] $s[2] 2 }
