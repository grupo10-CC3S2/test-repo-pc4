import os
import subprocess
import sys
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional


class MetricCollector:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self.metrics_dir = "metrics"
        self._ensure_directories()

    def _ensure_directories(self):
        os.makedirs(self.metrics_dir, exist_ok=True)

    def collect_pod_metrics(self) -> Dict:
        print(f"Recolectando métricas de pods en namespace: {self.namespace}")
        try:
            result = subprocess.run(
                ["kubectl", "top", "pods", "-n", self.namespace, "--no-headers"],
                capture_output=True, text=True, check=True
            )

            metrics = []
            timestamp = datetime.now().isoformat()

            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    metrics.append({
                        "timestamp": timestamp,
                        "pod_name": parts[0],
                        "cpu": parts[1],
                        "memory": parts[2],
                        "namespace": self.namespace
                    })
                    print(f"Pod {parts[0]}: CPU={parts[1]}, Memory={parts[2]}")

            return {
                "timestamp": timestamp,
                "namespace": self.namespace,
                "metrics": metrics,
                "type": "pod_metrics",
                "total_pods": len(metrics)
            }
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener métricas de pods: {e.stderr}")
            return {"metrics": [], "error": str(e), "type": "pod_metrics"}

    def collect_node_metrics(self) -> Dict:
        print("Recolectando métricas de nodos")
        try:
            result = subprocess.run(
                ["kubectl", "top", "nodes", "--no-headers"],
                capture_output=True, text=True, check=True
            )

            metrics = []
            timestamp = datetime.now().isoformat()

            for line in result.stdout.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    metrics.append({
                        "timestamp": timestamp,
                        "node_name": parts[0],
                        "cpu": parts[1],
                        "cpu_percent": parts[2],
                        "memory": parts[3],
                        "memory_percent": parts[4]
                    })
                    print(f"Node {parts[0]}: CPU={parts[1]}({parts[2]}), Memory={parts[3]}({parts[4]})")

            return {
                "timestamp": timestamp,
                "metrics": metrics,
                "type": "node_metrics",
                "total_nodes": len(metrics)
            }
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener métricas de nodos: {e.stderr}")
            return {"metrics": [], "error": str(e), "type": "node_metrics"}

    def save_metrics_json(self, metrics: Dict, filename: str):
        filepath = f"{self.metrics_dir}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"Métricas JSON guardadas en {filepath}")

    def save_metrics_csv(self, metrics: Dict, filename: str):
        if not metrics.get("metrics"):
            print(f"No hay métricas para guardar en CSV: {filename}")
            return

        filepath = f"{self.metrics_dir}/{filename}"
        fieldnames = metrics["metrics"][0].keys()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metrics["metrics"])
        print(f"Métricas CSV guardadas en {filepath}")

    def save_all_formats(self, metrics: Dict, base_filename: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{base_filename}_{timestamp}.json"
        csv_filename = f"{base_filename}_{timestamp}.csv"

        self.save_metrics_json(metrics, json_filename)
        self.save_metrics_csv(metrics, csv_filename)


def main():
    namespace = sys.argv[1] if len(sys.argv) > 1 else "default"

    print("Iniciando recolección de métricas de Kubernetes")
    print(f"Namespace: {namespace}")
    print("-" * 50)

    collector = MetricCollector(namespace)

    # Recolectar métricas de pods
    pod_metrics = collector.collect_pod_metrics()
    if pod_metrics.get("metrics"):
        collector.save_all_formats(pod_metrics, "pod_metrics")
        print(f"Recolectadas métricas de {pod_metrics['total_pods']} pods")
    else:
        print("No se pudieron recolectar métricas de pods")

    print("-" * 30)

    # Recolectar métricas de nodos
    node_metrics = collector.collect_node_metrics()
    if node_metrics.get("metrics"):
        collector.save_all_formats(node_metrics, "node_metrics")
        print(f"Recolectadas métricas de {node_metrics['total_nodes']} nodos")
    else:
        print("No se pudieron recolectar métricas de nodos")

    print("-" * 50)
    print("Recolección de métricas completada")


if __name__ == "__main__":
    main()
