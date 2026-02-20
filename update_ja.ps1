$content = Get-Content -Path "d:\MNY\rcubetech.github.io\index.html" -Raw
# Find the footerDevelopedBy inside the ja: block
$target = 'footerDevelopedBy: "Developed by <strong>rcubetech</strong>"'
$replacement = 'footerDevelopedBy: "Developed by <strong>rcubetech</strong>",
                contactTitle: "お問い合わせ",
                contactDesc: "ご質問やフィードバックがありますか？お気軽にご連絡ください。",
                contactNameLabel: "お名前",
                contactNamePlace: "お名前を入力",
                contactEmailLabel: "メールアドレス",
                contactEmailPlace: "example@email.com",
                contactMessageLabel: "メッセージ",
                contactMessagePlace: "どのようなご用件でしょうか？",
                btnSubmit: "メッセージを送信"'

# Since we know ja is at the end, we replace the LAST occurrence of DevelopedBy
$index = $content.LastIndexOf($target)
if ($index -ne -1) {
    $content = $content.Remove($index, $target.Length).Insert($index, $replacement)
    Set-Content -Path "d:\MNY\rcubetech.github.io\index.html" -Value $content -Encoding UTF8
    Write-Host "Japanese translation updated successfully."
} else {
    Write-Error "Target string not found."
}
