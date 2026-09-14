import re

with open('templates/index.html', 'r') as f:
    html = f.read()

config_addition = '''
                    typography: {
                        DEFAULT: {
                            css: {
                                color: '#828282',
                                h1: { color: '#f5f5f0', fontFamily: '"JetBrains Mono", monospace', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid #ff2e2e', paddingBottom: '0.5em', marginBottom: '1em' },
                                h2: { color: '#ff2e2e', fontFamily: '"JetBrains Mono", monospace', fontWeight: '600', textTransform: 'uppercase', marginTop: '2em', marginBottom: '1em', letterSpacing: '0.05em' },
                                h3: { color: '#f5f5f0', fontFamily: '"JetBrains Mono", monospace', fontWeight: '500' },
                                strong: { color: '#f5f5f0' },
                                a: { color: '#ff2e2e', textDecoration: 'none', borderBottom: '1px dashed #ff2e2e', '&:hover': { color: '#ffffff', borderBottomStyle: 'solid' } },
                                blockquote: { borderLeftColor: '#ff2e2e', color: '#828282', fontStyle: 'normal', backgroundColor: '#111111', padding: '1em' },
                                code: { color: '#ff2e2e', backgroundColor: '#111111', padding: '0.2em 0.4em', borderRadius: '2px', fontWeight: '400' },
                                'code::before': { content: '""' },
                                'code::after': { content: '""' },
                                hr: { borderColor: '#242424' },
                            }
                        }
                    }'''

html = re.sub(
    r'(fontFamily: \{\s*sans: \[\'"Space Grotesk"\', \'sans-serif\'\],\s*mono: \[\'"JetBrains Mono"\', \'monospace\'\],\s*\})', 
    r'\1,' + config_addition, 
    html, 
    flags=re.DOTALL
)

with open('templates/index.html', 'w') as f:
    f.write(html)
print("Patched Tailwind typography config!")
