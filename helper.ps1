$Src = "Text to Speech gtts"
$Zipped = "Text to Speech gtts.zip"
$Addon = "C:\Users\marco\AppData\Roaming\Blender Foundation\Blender\3.1\scripts\addons\Text to Speech"

Set-Location -Path "C:\Users\marco\blender-text-to-speech-gtts"

if (Test-Path $Zipped) 
{
  Remove-Item $Zipped
  Compress-Archive -Path $Src -DestinationPath $Zipped
}
else
{
	Compress-Archive -Path $Src -DestinationPath $Zipped
}

if (Test-Path $Addon)
{
  Remove-Item -Recurse $Addon
}