#!/usr/bin/env python3
"""
Sistema de Monitoramento de Threads
Monitora performance, memória e status de cada thread individualmente
"""

import threading
import time
import psutil
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from support.logger import Logger


@dataclass
class ThreadStats:
    """Estatísticas de uma thread individual"""
    thread_id: int
    thread_name: str
    is_alive: bool
    cpu_percent: float
    memory_mb: float
    status: str
    last_activity: str
    iterations: int
    errors: int
    warnings: int


@dataclass
class SystemStats:
    """Estatísticas gerais do sistema"""
    total_threads: int
    active_threads: int
    total_memory_mb: float
    total_cpu_percent: float
    timestamp: str


class ThreadMonitor:
    """Monitor de threads com métricas detalhadas"""
    
    def __init__(self):
        self._logger = Logger()
        self._monitored_threads: Dict[str, Dict[str, Any]] = {}
        self._thread_stats: Dict[str, ThreadStats] = {}
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Contadores por thread
        self._thread_counters: Dict[str, Dict[str, int]] = {}
        
    def register_thread(self, thread_name: str, thread_obj: threading.Thread, 
                       thread_type: str = "unknown", description: str = "") -> None:
        """Registra uma thread para monitoramento"""
        with self._lock:
            self._monitored_threads[thread_name] = {
                'thread': thread_obj,
                'type': thread_type,
                'description': description,
                'start_time': time.time(),
                'last_activity': time.time(),
                'iterations': 0,
                'errors': 0,
                'warnings': 0
            }
            
            self._thread_counters[thread_name] = {
                'iterations': 0,
                'errors': 0,
                'warnings': 0,
                'last_reset': time.time()
            }
            
        self._logger.info(f"Thread registrada para monitoramento: {thread_name} ({thread_type})")
    
    def increment_counter(self, thread_name: str, counter_type: str = "iterations") -> None:
        """Incrementa contador de uma thread"""
        if thread_name in self._thread_counters:
            self._thread_counters[thread_name][counter_type] += 1
            self._thread_counters[thread_name]['last_activity'] = time.time()
    
    def get_thread_stats(self, thread_name: str) -> Optional[ThreadStats]:
        """Obtém estatísticas de uma thread específica"""
        with self._lock:
            if thread_name not in self._monitored_threads:
                return None
                
            thread_info = self._monitored_threads[thread_name]
            thread_obj = thread_info['thread']
            
            # Obtém informações do processo atual
            process = psutil.Process(os.getpid())
            
            # Calcula uso de memória da thread (aproximado)
            memory_mb = process.memory_info().rss / 1024 / 1024 / len(threading.enumerate())
            
            # Calcula CPU da thread (aproximado)
            cpu_percent = process.cpu_percent() / len(threading.enumerate())
            
            return ThreadStats(
                thread_id=thread_obj.ident or 0,
                thread_name=thread_name,
                is_alive=thread_obj.is_alive(),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                status="running" if thread_obj.is_alive() else "stopped",
                last_activity=datetime.fromtimestamp(
                    self._thread_counters[thread_name]['last_activity']
                ).strftime("%H:%M:%S"),
                iterations=self._thread_counters[thread_name]['iterations'],
                errors=self._thread_counters[thread_name]['errors'],
                warnings=self._thread_counters[thread_name]['warnings']
            )
    
    def get_all_thread_stats(self) -> List[ThreadStats]:
        """Obtém estatísticas de todas as threads monitoradas"""
        stats = []
        for thread_name in self._monitored_threads.keys():
            thread_stats = self.get_thread_stats(thread_name)
            if thread_stats:
                stats.append(thread_stats)
        return stats
    
    def get_system_stats(self) -> SystemStats:
        """Obtém estatísticas gerais do sistema"""
        process = psutil.Process(os.getpid())
        all_threads = threading.enumerate()
        
        return SystemStats(
            total_threads=len(all_threads),
            active_threads=len([t for t in all_threads if t.is_alive()]),
            total_memory_mb=process.memory_info().rss / 1024 / 1024,
            total_cpu_percent=process.cpu_percent(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def start_monitoring(self, interval: int = 30) -> None:
        """Inicia monitoramento contínuo"""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True,
            name="ThreadMonitor"
        )
        self._monitor_thread.start()
        self._logger.info(f"Monitoramento de threads iniciado (intervalo: {interval}s)")
    
    def stop_monitoring(self) -> None:
        """Para o monitoramento"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self._logger.info("Monitoramento de threads parado")
    
    def _monitoring_loop(self, interval: int) -> None:
        """Loop principal de monitoramento"""
        while self._monitoring_active:
            try:
                self._log_thread_status()
                time.sleep(interval)
            except Exception as e:
                self._logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(interval)
    
    def _log_thread_status(self) -> None:
        """Loga status de todas as threads"""
        system_stats = self.get_system_stats()
        thread_stats = self.get_all_thread_stats()
        
        self._logger.info(f"=== STATUS DAS THREADS ===")
        self._logger.info(f"Sistema: {system_stats.total_threads} threads, "
                         f"{system_stats.total_memory_mb:.1f}MB, "
                         f"{system_stats.total_cpu_percent:.1f}% CPU")
        
        for stats in thread_stats:
            self._logger.info(f"  {stats.thread_name}: "
                             f"{'ALIVE' if stats.is_alive else 'DEAD'}, "
                             f"{stats.memory_mb:.1f}MB, "
                             f"{stats.iterations} iterações, "
                             f"{stats.errors} erros")
    
    def export_stats(self, filename: str = None) -> str:
        """Exporta estatísticas para arquivo JSON"""
        if filename is None:
            filename = f"thread_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'system': asdict(self.get_system_stats()),
            'threads': [asdict(stats) for stats in self.get_all_thread_stats()],
            'export_time': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        self._logger.info(f"Estatísticas exportadas para: {filename}")
        return filename
    
    def get_thread_summary(self) -> Dict[str, Any]:
        """Retorna resumo das threads para API"""
        return {
            'system': asdict(self.get_system_stats()),
            'threads': [asdict(stats) for stats in self.get_all_thread_stats()],
            'monitoring_active': self._monitoring_active
        }


# Instância global do monitor
thread_monitor = ThreadMonitor()
