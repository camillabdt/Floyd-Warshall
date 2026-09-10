import argparse
import sys
from floyd_warshall.application.floyd_warshall_solver import FloydWarshallSolver, NegativeCycleError
from floyd_warshall.infrastructure.text_graph_reader import TextGraphReader
from floyd_warshall.presentation.console_renderer import ConsoleRenderer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Caminhos mínimos entre todos os pares com Floyd-Warshall.'
    )
    parser.add_argument('arquivo', help='Arquivo: origem destino peso')
    parser.add_argument('--origem', help='Vértice de origem para consulta')
    parser.add_argument('--destino', help='Vértice de destino para consulta')
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if bool(args.origem) != bool(args.destino):
        parser.error('--origem e --destino devem ser informados juntos.')

    # Composition Root: dependências concretas são conectadas apenas aqui.
    reader = TextGraphReader()
    solver = FloydWarshallSolver()
    renderer = ConsoleRenderer()

    try:
        graph = reader.read(args.arquivo)
        result = solver.solve(graph)
        renderer.render(result)
        if args.origem and args.destino:
            renderer.render_query(result, args.origem, args.destino)
    except (FileNotFoundError, ValueError, NegativeCycleError) as exc:
        print(f'Erro: {exc}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
