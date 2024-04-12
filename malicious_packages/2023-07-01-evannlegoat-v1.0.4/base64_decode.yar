rule method_base64_b64decode
{
    strings:
        $text = "base64.b64decode("

    condition:
        $text
}
