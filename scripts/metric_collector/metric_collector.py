import os
import subprocess
import sys
import json
import csv
from typing import List, Dict

class MetricCollector:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.metrics_dir = "metrics"
        self._ensure_directories()
    
    def _ensure_directories(self):
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def collect_pod_metrics(self) -> List[Dict]:
        print(f"Recolectando métricas de pods en namespace: {self.namespace}")
        try:
            result = subprocess.run(
                ["kubectl", "top", "pods", "-n", self.namespace, "--no-headers"],
                capture_output=True, text=True, check=True
            )
            
            metrics = []
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    metrics.append({
                        "NAME": parts[0],
                        "CPU(cores)": parts[1],
                        "MEMORY(bytes)": parts[2]
                    })
            
            return metrics
        except subprocess.CalledProcessError as e:
            print(f" Error al obtener métricas de pods: {e.stderr}")
            return []
    
    def collect_node_metrics(self) -> List[Dict]:
        print("Recolectando métricas de nodos")
        try:
            result = subprocess.run(
                ["kubectl", "top", "nodes", "--no-headers"],
                capture_output=True, text=True, check=True
            )
            
            metrics = []
            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    metrics.append({
                        "NAME": parts[0],
                        "CPU(cores)": parts[1],
                        "CPU(%)": parts[2],
                        "MEMORY(bytes)": parts[3],
                        "MEMORY(%)": parts[4]
                    })
            
            return metrics
        except subprocess.CalledProcessError as e:
            print(f" Error al obtener métricas de nodos: {e.stderr}")
            return []
    
    def save_pod_metrics_csv(self, metrics: List[Dict]):
        if not metrics:
            print("  No hay métricas de pods para guardar")
            return
            
        filepath = f"{self.metrics_dir}/pod_metrics.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["NAME", "CPU(cores)", "MEMORY(bytes)"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics)
        print(f" Métricas de pods CSV guardadas en {filepath}")
    
    def save_node_metrics_csv(self, metrics: List[Dict]):
        if not metrics:
            print("  No hay métricas de nodos para guardar")
            return
            
        filepath = f"{self.metrics_dir}/node_metrics.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["NAME", "CPU(cores)", "CPU(%)", "MEMORY(bytes)", "MEMORY(%)"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics)
        print(f" Métricas de nodos CSV guardadas en {filepath}")
    
    def save_pod_metrics_json(self, metrics: List[Dict]):
        if not metrics:
            print("  No hay métricas de pods para guardar")
            return
            
        filepath = f"{self.metrics_dir}/pod_metrics.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f" Métricas de pods JSON guardadas en {filepath}")
    
    def save_node_metrics_json(self, metrics: List[Dict]):
        if not metrics:
            print("  No hay métricas de nodos para guardar")
            return
            
        filepath = f"{self.metrics_dir}/node_metrics.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f" Métricas de nodos JSON guardadas en {filepath}")

def main():
    namespace = sys.argv[1] if len(sys.argv) > 1 else "default"
    
    print("Iniciando recolección de métricas de Kubernetes")
    print(f"Namespace: {namespace}")
    print("-" * 50)
    
    collector = MetricCollector(namespace)
    
    # Recolectar métricas de pods
    pod_metrics = collector.collect_pod_metrics()
    if pod_metrics:
        collector.save_pod_metrics_csv(pod_metrics)
        collector.save_pod_metrics_json(pod_metrics)
        print(f" Recolección de métricas de {len(pod_metrics)} pods")
    
    print("-" * 50)
    
    # Recolectar métricas de nodos
    node_metrics = collector.collect_node_metrics()
    if node_metrics:
        collector.save_node_metrics_csv(node_metrics)
        collector.save_node_metrics_json(node_metrics)
        print(f" Recolección de métricas de {len(node_metrics)} nodo(s)")
    
    print("-" * 50)
    print("Recolección de métricas completada")

if __name__ == "__main__":
    main()
