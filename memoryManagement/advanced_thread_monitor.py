#!/usr/bin/env python3
"""
Monitor Avançado de Threads
Monitora threads individuais com métricas detalhadas e alertas
"""

import psutil
import time
import json
import threading
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse


class AdvancedThreadMonitor:
    """Monitor avançado de threads com alertas e métricas"""

    def __init__(self, target_pid: Optional[int] = None):
        self.target_pid = target_pid or self._find_titanium_process()
        self.monitoring = False
        self.thread_history: Dict[str, List[Dict]] = {}
        self.alerts: List[Dict] = []
        self.start_time = datetime.now()

        if not self.target_pid:
            print("❌ Processo TitaniumServer não encontrado!")
            sys.exit(1)

        print(f"✅ Monitorando processo PID: {self.target_pid}")

    def _find_titanium_process(self) -> Optional[int]:
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

    def get_thread_info(self) -> List[Dict]:
        """Obtém informações detalhadas de todas as threads"""
        try:
            process = psutil.Process(self.target_pid)
            threads = []

            for thread in process.threads():
                thread_info = {
                    'id': thread.id,
                    'user_time': thread.user_time,
                    'system_time': thread.system_time,
                    'status': 'active' if thread.user_time > 0 or thread.system_time > 0 else 'idle'
                }
                threads.append(thread_info)

            return threads
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"❌ Erro ao acessar processo: {e}")
            return []

    def get_process_stats(self) -> Dict:
        """Obtém estatísticas do processo principal"""
        try:
            process = psutil.Process(self.target_pid)
            return {
                'pid': process.pid,
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'create_time': datetime.fromtimestamp(process.create_time()),
                'status': process.status()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}

    def analyze_thread_health(self, thread_data: List[Dict]) -> List[Dict]:
        """Analisa saúde das threads e gera alertas"""
        alerts = []

        # Verifica threads com alto uso de CPU
        for thread in thread_data:
            if thread['user_time'] > 10.0:  # 10 segundos de CPU
                alerts.append({
                    'type': 'high_cpu',
                    'thread_id': thread['id'],
                    'message': f"Thread {thread['id']} com alto uso de CPU: {thread['user_time']:.2f}s",
                    'severity': 'warning'
                })

        # Verifica threads inativas
        idle_threads = [t for t in thread_data if t['status'] == 'idle']
        if len(idle_threads) > len(thread_data) * 0.8:  # 80% das threads inativas
            alerts.append({
                'type': 'too_many_idle',
                'message': f"Muitas threads inativas: {len(idle_threads)}/{len(thread_data)}",
                'severity': 'info'
            })

        return alerts

    def monitor_loop(self, interval: int = 5, duration: int = 300):
        """Loop principal de monitoramento"""
        print(
            f"🔄 Iniciando monitoramento (intervalo: {interval}s, duração: {duration}s)")

        self.monitoring = True
        end_time = time.time() + duration

        while self.monitoring and time.time() < end_time:
            try:
                # Coleta dados
                process_stats = self.get_process_stats()
                thread_data = self.get_thread_info()

                if not process_stats:
                    print("❌ Processo não encontrado, parando monitoramento")
                    break

                # Analisa saúde
                alerts = self.analyze_thread_health(thread_data)
                self.alerts.extend(alerts)

                # Armazena histórico
                timestamp = datetime.now()
                for thread in thread_data:
                    thread_id = str(thread['id'])
                    if thread_id not in self.thread_history:
                        self.thread_history[thread_id] = []

                    self.thread_history[thread_id].append({
                        'timestamp': timestamp.isoformat(),
                        'user_time': thread['user_time'],
                        'system_time': thread['system_time'],
                        'status': thread['status']
                    })

                # Exibe status
                self._display_status(process_stats, thread_data, alerts)

                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n⏹️  Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(interval)

        self.monitoring = False
        self._generate_report()

    def _display_status(self, process_stats: Dict, thread_data: List[Dict], alerts: List[Dict]):
        """Exibe status atual"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\r⏰ {timestamp} | "
              f"PID: {process_stats['pid']} | "
              f"Threads: {process_stats['num_threads']} | "
              f"Mem: {process_stats['memory_mb']:.1f}MB | "
              f"CPU: {process_stats['cpu_percent']:.1f}% | "
              f"Alertas: {len(alerts)}", end="", flush=True)

        # Exibe alertas críticos
        critical_alerts = [a for a in alerts if a['severity'] == 'warning']
        if critical_alerts:
            print(f"\n⚠️  {critical_alerts[0]['message']}")

    def _generate_report(self):
        """Gera relatório final"""
        print("\n\n📊 RELATÓRIO DE MONITORAMENTO")
        print("=" * 50)

        # Estatísticas gerais
        duration = datetime.now() - self.start_time
        print(f"⏱️  Duração: {duration}")
        print(f"🧵 Threads monitoradas: {len(self.thread_history)}")
        print(f"⚠️  Total de alertas: {len(self.alerts)}")

        # Top threads por uso de CPU
        print("\n🔥 Top 5 threads por uso de CPU:")
        thread_totals = {}
        for thread_id, history in self.thread_history.items():
            total_cpu = sum(entry['user_time'] + entry['system_time']
                            for entry in history)
            thread_totals[thread_id] = total_cpu

        sorted_threads = sorted(thread_totals.items(),
                                key=lambda x: x[1], reverse=True)
        for i, (thread_id, cpu_time) in enumerate(sorted_threads[:5]):
            print(f"  {i+1}. Thread {thread_id}: {cpu_time:.2f}s")

        # Alertas por tipo
        alert_types = {}
        for alert in self.alerts:
            alert_type = alert['type']
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1

        if alert_types:
            print("\n⚠️  Alertas por tipo:")
            for alert_type, count in alert_types.items():
                print(f"  - {alert_type}: {count}")

        # Salva relatório
        self._save_report()

    def _save_report(self):
        """Salva relatório em arquivo JSON"""
        report = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'threads_monitored': len(self.thread_history),
            'total_alerts': len(self.alerts),
            'thread_history': self.thread_history,
            'alerts': self.alerts
        }

        filename = f"thread_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Relatório salvo em: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Monitor Avançado de Threads')
    parser.add_argument('--interval', '-i', type=int, default=5,
                        help='Intervalo de monitoramento em segundos (padrão: 5)')
    parser.add_argument('--duration', '-d', type=int, default=300,
                        help='Duração do monitoramento em segundos (padrão: 300)')
    parser.add_argument('--pid', '-p', type=int, default=None,
                        help='PID do processo a monitorar (padrão: auto-detecta)')

    args = parser.parse_args()

    print("🧵 Monitor Avançado de Threads - TitaniumServer")
    print("=" * 50)

    monitor = AdvancedThreadMonitor(args.pid)
    monitor.monitor_loop(args.interval, args.duration)


if __name__ == "__main__":
    main()
