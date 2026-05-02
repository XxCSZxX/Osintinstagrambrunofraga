`nmap -sS -T0 -f -D RND:50,ME -Pn -O -sV -p- --script vuln --data-length 256 --ttl 129 --spoof-mac AA:BB:CC:DD:EE:FF --badsum --proxies http://proxy1,http://proxy2 -S <IP_falso> -e <interface_rede> -oN stealth_vuln_scan.txt <alvo>`

- Mais decoys (`RND:50`)
- Dados aleatórios maiores (`256`)
- TTL alterado (`129`)
- Passa por proxies (`--proxies`)
- IP de origem falso (`-S`)
- Interface de rede específica (`-e`)

⚠️ Máximo stealth. Ajuste `<alvo>`, `<IP_falso>` e `<interface_rede>`. Uso avançado 😎.
