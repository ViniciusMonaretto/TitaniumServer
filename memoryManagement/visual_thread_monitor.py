#!/usr/bin/env python3
"""
Monitor Visual de Threads
Interface visual para monitorar threads em tempo real
"""

import psutil
import time
import os
import sys
from datetime import datetime
import argparse


class VisualThreadMonitor:
    """Monitor visual de threads com interface de terminal"""

    def __init__(self, target_pid=None):
        self.target_pid = target_pid or self._find_titanium_process()
        self.running = False

        if not self.target_pid:
            print("❌ Processo TitaniumServer não encontrado!")
            sys.exit(1)

    def _find_titanium_process(self):
        """Encontra o processo Python do TitaniumServer"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'main.py' in cmdline or 'server' in cmdline:
                        return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def clear_screen(self):
        """Limpa a tela"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def get_thread_info(self):
        """Obtém informações das threads"""
        try:
            process = psutil.Process(self.target_pid)
            threads = []

            for thread in process.threads():
                threads.append({
                    'id': thread.id,
                    'user_time': thread.user_time,
                    'system_time': thread.system_time,
                    'total_time': thread.user_time + thread.system_time
                })

            return sorted(threads, key=lambda x: x['total_time'], reverse=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []

    def get_process_info(self):
        """Obtém informações do processo"""
        try:
            process = psutil.Process(self.target_pid)
            return {
                'pid': process.pid,
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time())
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def display_header(self, process_info):
        """Exibe cabeçalho com informações do processo"""
        if not process_info:
            return

        print("🧵 MONITOR VISUAL DE THREADS - TitaniumServer")
        print("=" * 60)
        print(f"📊 PID: {process_info['pid']} | "
              f"Status: {process_info['status']} | "
              f"Threads: {process_info['num_threads']}")
        print(f"💾 Memória: {process_info['memory_mb']:.1f}MB | "
              f"CPU: {process_info['cpu_percent']:.1f}% | "
              f"Iniciado: {process_info['create_time'].strftime('%H:%M:%S')}")
        print("=" * 60)

    def display_threads(self, threads):
        """Exibe informações das threads"""
        print(
            f"{'ID':<8} {'CPU User':<10} {'CPU Sys':<10} {'Total':<10} {'Status':<10}")
        print("-" * 60)

        for thread in threads[:20]:  # Mostra top 20 threads
            status = "🔥" if thread['total_time'] > 1.0 else "⚡" if thread['total_time'] > 0.1 else "💤"

            print(f"{thread['id']:<8} "
                  f"{thread['user_time']:<10.2f} "
                  f"{thread['system_time']:<10.2f} "
                  f"{thread['total_time']:<10.2f} "
                  f"{status:<10}")

        if len(threads) > 20:
            print(f"... e mais {len(threads) - 20} threads")

    def display_summary(self, threads, process_info):
        """Exibe resumo das threads"""
        if not threads or not process_info:
            return

        total_cpu = sum(t['total_time'] for t in threads)
        active_threads = len([t for t in threads if t['total_time'] > 0.1])
        idle_threads = len(threads) - active_threads

        print("\n📈 RESUMO:")
        print(f"   Total de threads: {len(threads)}")
        print(f"   Threads ativas: {active_threads}")
        print(f"   Threads inativas: {idle_threads}")
        print(f"   CPU total: {total_cpu:.2f}s")
        print(f"   Memória: {process_info['memory_mb']:.1f}MB")

        # Threads mais ativas
        top_threads = [t for t in threads[:3] if t['total_time'] > 0]
        if top_threads:
            print(
                f"   Top threads: {', '.join(str(t['id']) for t in top_threads)}")

    def run(self, interval=2):
        """Executa o monitor visual"""
        self.running = True
        print("🔄 Iniciando monitor visual... (Ctrl+C para sair)")
        time.sleep(1)

        try:
            while self.running:
                self.clear_screen()

                process_info = self.get_process_info()
                threads = self.get_thread_info()

                if not process_info:
                    print("❌ Processo não encontrado!")
                    break

                self.display_header(process_info)
                self.display_threads(threads)
                self.display_summary(threads, process_info)

                print(
                    f"\n⏰ Atualizado em: {datetime.now().strftime('%H:%M:%S')}")
                print("💡 Pressione Ctrl+C para sair")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n⏹️  Monitor interrompido pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
        finally:
            self.running = False


def main():
    parser = argparse.ArgumentParser(description='Monitor Visual de Threads')
    parser.add_argument('--interval', '-i', type=int, default=2,
                        help='Intervalo de atualização em segundos (padrão: 2)')
    parser.add_argument('--pid', '-p', type=int, default=None,
                        help='PID do processo a monitorar (padrão: auto-detecta)')

    args = parser.parse_args()

    monitor = VisualThreadMonitor(args.pid)
    monitor.run(args.interval)


if __name__ == "__main__":
    main()
