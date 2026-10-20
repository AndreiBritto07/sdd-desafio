"""CLI: python -m src calcular --input ... --output ... --politica ... --cambio ..."""
import argparse
import sys
from pathlib import Path
from .motor import parse, executar, serializar
from .validacao_global import ErroGlobal, falha

def main(argv=None):
    parser = argparse.ArgumentParser(description='Motor de reembolso')
    sub = parser.add_subparsers(dest='comando', required=True)
    cmd = sub.add_parser('calcular')
    for flag in ('input', 'output', 'politica', 'cambio'):
        cmd.add_argument('--' + flag, required=True)
    args = parser.parse_args(argv)
    try:
        try: entrada = Path(args.input).read_text(encoding='utf-8')
        except OSError as e: raise ErroGlobal('ERRO_IO', str(e)) from e
        dados = parse(entrada, 'JSON_INVALIDO')
        # Falhas do envelope devem prevalecer sobre arquivos externos.
        from .validacao_global import validar_envelope
        validar_envelope(dados)
        def externo(path, codigo):
            try: texto = Path(path).read_text(encoding='utf-8')
            except (OSError, UnicodeError) as e: raise ErroGlobal(codigo, str(e)) from e
            return parse(texto, codigo)
        politica = externo(args.politica, 'POLITICA_INVALIDA')
        cambio = externo(args.cambio, 'CAMBIO_INVALIDO')
        resultado = executar(dados, politica, cambio)
        codigo = 0
    except ErroGlobal as e:
        resultado = falha(e)
        codigo = 3 if e.codigo == 'ERRO_IO' else 2
    except UnicodeError as e:
        resultado = falha(ErroGlobal('JSON_INVALIDO', str(e)))
        codigo = 2
    try:
        Path(args.output).write_text(serializar(resultado), encoding='utf-8')
    except OSError as e:
        print(f'ERRO_IO: {e}', file=sys.stderr)
        return 3
    return codigo

if __name__ == '__main__':
    sys.exit(main())
