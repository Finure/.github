from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.saas.cdn import Cloudflare
from diagrams.gcp.network import NAT, LoadBalancing
from diagrams.gcp.storage import Storage
from diagrams.onprem.network import Istio
from diagrams.k8s.compute import Pod, StatefulSet, Job
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.chaos import ChaosMesh
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Prometheus, Grafana
from diagrams.onprem.logging import Loki, Fluentbit
from diagrams.k8s.ecosystem import ExternalDns, Helm, Kustomize
from diagrams.onprem.gitops import Flux, Argocd
from diagrams.saas.chat import Slack
from diagrams.onprem.vcs import Github
from diagrams.onprem.queue import Kafka
from diagrams.onprem.security import Vault, Trivy
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.cd import Tekton
from diagrams.onprem.iac import Terraform
from diagrams.custom import Custom

# Custom icons
KServeIcon = lambda label: Custom(label, "./icons/kserve.png")
KnativeIcon = lambda label: Custom(label, "./icons/knative.png")
CNPGOperIcon = lambda label: Custom(label, "./icons/cnpg-operator.png")
ESOIcon = lambda label: Custom(label, "./icons/external-secrets.png")
KyvernoIcon = lambda label: Custom(label, "./icons/kyverno.png")
VeleroIcon = lambda label: Custom(label, "./icons/velero.png")
KialiIcon = lambda label: Custom(label, "./icons/kiali.png")
CertMgrIcon = lambda label: Custom(label, "./icons/cert-manager.png")
SonarIcon = lambda label: Custom(label, "./icons/sonarqube.png")
SnykIcon = lambda label: Custom(label, "./icons/snyk.png")
OpenCostIcon = lambda label: Custom(label, "./icons/opencost.png")
KaggleIcon = lambda label: Custom(label, "./icons/kaggle.png")
KEDAIcon = lambda label: Custom(label, "./icons/keda.png")
BeylaIcon = lambda label: Custom(label, "./icons/beyla.png")
OtelIcon = lambda label: Custom(label, "./icons/otel.png")
SignozIcon = lambda label: Custom(label, "./icons/signoz.png")
K8sGatewayIcon = lambda label: Custom(label, "./icons/k8s-gateway-api.png")
FlaggerIcon = lambda label: Custom(label, "./icons/flagger.png")

with Diagram(
    "Finure high level workflow",
    filename="finure_arch",
    outformat="png",
    show=False,
    graph_attr={
        "rankdir": "LR",
        "splines": "spline",
        "pad": "0.3",
        "nodesep": "0.55",
        "ranksep": "0.9",
        "fontname": "Inter",
    },
):
    user = Users("User")
    cloudflare = Cloudflare("Cloudflare")
    nlb = LoadBalancing("Network LB")
    gcs_raw = Storage("GCS Raw Data")
    gcs_formatted = Storage("GCS Formatted Data")
    gcs_models = Storage("GCS Models")
    gcs_logs = Storage("GCS Logs")
    gcs_bkp = Storage("GCS Backups")
    slack = Slack("Slack")
    github = Github("GitHub Repo")
    ghcr = Github("GHCR")
    terraform = Terraform("Terraform")
    kaggle = KaggleIcon("Kaggle")
    seed_job = Job("seed-job (bootstrap)")

    with Cluster("Cluster"):
        cloud_nat = NAT("Cloud NAT")
        
        with Cluster("Ingress Layer", graph_attr={"style": "dashed"}):
            k8s_gateway = K8sGatewayIcon("K8s Gateway API")
            istio_controller = Istio("Istio Controller")
        
        fe_pod = Pod("frontend-pod")
        mw_pod = Pod("middleware-pod")
        kafka = Kafka("Kafka Cluster")
        be_pod = Pod("backend-pod")
        kserve_pod = KServeIcon("KServe")
        hpa_fe = HPA("HPA: frontend")
        hpa_mw = HPA("HPA: middleware")
        hpa_kserve = HPA("HPA: kserve")
        keda = KEDAIcon("KEDA (Kafka scaler)")
        knative = KnativeIcon("Knative Serving")
        cnpg = StatefulSet("PostgreSQL Cluster (3 replicas)")
        postgres = PostgreSQL("Postgres DB")
        cnpg_op = CNPGOperIcon("CNPG Operator")
        prom = Prometheus("Prometheus")
        graf = Grafana("Grafana")
        loki = Loki("Loki")
        fluentbit = Fluentbit("Fluent Bit")
        kiali = KialiIcon("Kiali")
        certmgr = CertMgrIcon("cert-manager")
        extdns = ExternalDns("external-dns")
        eso = ESOIcon("External Secrets Operator")
        kyverno = KyvernoIcon("Kyverno")
        velero = VeleroIcon("Velero")
        flux = Flux("Flux")
        kustomize = Kustomize("Kustomize")
        vault = Vault("Vault")
        opencost = OpenCostIcon("OpenCost")
        airflow = Airflow("Airflow DAG")
        argo_events = Argocd("Argo Events")
        argo_workflows = Argocd("Argo Workflows")
        tekton = Tekton("Tekton")
        sonar = SonarIcon("SonarQube")
        trivy = Trivy("Trivy")
        snyk = SnykIcon("Snyk")
        helm = Helm("Helm")
        cluster_node = Custom("", "./icons/gke-cluster.png")
        
        beyla = BeylaIcon("Beyla")
        otel_collector = OtelIcon("OpenTelemetry Collector")
        signoz = SignozIcon("SigNoz")
        
        flagger = FlaggerIcon("Flagger")
        
        chaos_mesh = ChaosMesh("Chaos Mesh")

    user >> Edge(label="HTTPS") >> cloudflare >> nlb >> k8s_gateway
    k8s_gateway >> fe_pod >> Edge(label="HTTP") >> mw_pod
    
    # Entry
    k8s_gateway >> Edge(label="managed by", style="dashed", color="#888", dir="both") >> istio_controller
    mw_pod >> Edge(label="produce") >> kafka
    kafka >> Edge(label="consume") >> be_pod
    be_pod >> Edge(label="inference") >> kserve_pod
    kserve_pod >> Edge(label="serverless", style="dashed", color="#888") >> knative

    # App DB
    be_pod >> Edge(label="insert record") >> postgres
    cnpg >> Edge(label="manages", style="dashed", color="#888") >> postgres
    cnpg >> Edge(label="backups", style="dashed", color="#6a8caf") >> gcs_bkp
    cnpg_op >> Edge(style="dashed", color="#888") >> cnpg

    # seedjob
    kaggle >> Edge(label="download dataset", style="dashed", color="#4c8eda") >> seed_job
    seed_job >> Edge(label="validate & push seed data", style="dashed", color="#4c8eda") >> postgres

    # Data/ML pipeline
    gcs_raw >> Edge(label="new dataset", style="dashed", color="#6a8caf") >> airflow
    airflow >> Edge(label="save clean data", style="dashed", color="#6a8caf") >> gcs_formatted
    airflow >> Edge(label="event", style="dashed", color="#6a8caf") >> argo_events
    argo_events >> Edge(label="trigger", style="dashed", color="#6a8caf") >> argo_workflows
    argo_workflows >> Edge(label="read raw data", style="dashed", color="#6a8caf") >> gcs_formatted
    argo_workflows >> Edge(label="train & save model", style="dashed", color="#6a8caf") >> gcs_models
    gcs_models >> Edge(label="new model", style="dashed", color="#6a8caf") >> kserve_pod
    knative >> Edge(label="update", style="dashed", color="#6a8caf") >> kserve_pod

    # CI/CD
    github >> Edge(label="webhook", style="dashed", color="#7b8cde") >> tekton
    tekton >> Edge(label="static analysis", style="dashed", color="#7b8cde") >> sonar
    tekton >> Edge(label="image scan", style="dashed", color="#7b8cde") >> trivy
    tekton >> Edge(label="vuln scan", style="dashed", color="#7b8cde") >> snyk
    tekton >> Edge(label="update", style="dashed", color="#7b8cde") >> helm
    tekton >> Edge(label="push image", style="dashed", color="#7b8cde") >> ghcr
    tekton >> Edge(label="commit changes", style="dashed", color="#7b8cde") >> github
    flux >> Edge(label="uses", style="dashed", color="#7b8cde") >> kustomize
    flux >> Edge(label="flux deploy notifications", style="dashed", color="#7b8cde") >> slack
    tekton >> Edge(label="tekton pipeline notifications", style="dashed", color="#7b8cde") >> slack
    airflow >> Edge(label="airflow pipeline alerts", style="dashed", color="#7b8cde") >> slack

    # Progressive Delivery with Flagger
    flagger_edge = {"style": "dashed", "color": "#ff6b6b"}
    flagger >> Edge(label="blue/green progressive delivery", **flagger_edge) >> fe_pod
    flagger >> Edge(label="blue/green progressive delivery", **flagger_edge) >> mw_pod
    flagger >> Edge(label="blue/green progressive delivery", **flagger_edge) >> be_pod
    flagger >> Edge(label="works with", **flagger_edge) >> istio_controller

    # Auto-instrumentation with Beyla, OTel and SigNoz
    instrumentation_edge = {"style": "dashed", "color": "#00d4aa"}
    beyla >> Edge(label="auto-instrument", **instrumentation_edge) >> fe_pod
    beyla >> Edge(label="auto-instrument", **instrumentation_edge) >> mw_pod
    beyla >> Edge(label="auto-instrument", **instrumentation_edge) >> be_pod
    beyla >> Edge(label="send metrics", **instrumentation_edge) >> otel_collector
    otel_collector >> Edge(label="export to", **instrumentation_edge) >> signoz

    # Chaos Engineering
    chaos_edge = {"style": "dashed", "color": "#ff9500"}
    chaos_mesh >> Edge(label="chaos experiments", **chaos_edge) >> fe_pod
    chaos_mesh >> Edge(label="chaos experiments", **chaos_edge) >> mw_pod
    chaos_mesh >> Edge(label="chaos experiments", **chaos_edge) >> be_pod

    # Observability
    subtle = {"style": "dashed", "color": "#9aa4ad"}
    for w in [fe_pod, mw_pod, be_pod, kserve_pod]:
        w >> Edge(label="metrics scrape", **subtle) >> prom
        w >> Edge(label="logs", **subtle) >> fluentbit

    prom >> Edge(**subtle) >> graf
    fluentbit >> Edge(label="to Loki", **subtle) >> loki
    loki >> Edge(label="storage", **subtle) >> gcs_logs
    loki >> Edge(label="logs", **subtle) >> graf
    istio_controller >> Edge(label="mesh viz", **subtle) >> kiali
    opencost >> Edge(label="cost metrics", **subtle) >> prom

    # DNS/TLS
    certmgr >> Edge(label="DNS verification", **subtle) >> cloudflare
    extdns >> Edge(label="DNS records", **subtle) >> cloudflare

    # Secrets
    vault << Edge(label="fetch secrets", **subtle) << eso
    for w in [fe_pod, mw_pod, be_pod, postgres]:
        eso >> Edge(**subtle) >> w

    # Policy and backups
    kyverno >> Edge(label="validate/mutate", **subtle)
    for w in [fe_pod, mw_pod, be_pod, postgres, kserve_pod, knative]:
        kyverno >> Edge(label="policies", **subtle) >> w
    velero >> Edge(label="backup cluster", **subtle) >> gcs_bkp

    # Egress
    be_pod >> Edge(label="egress", style="dotted", color="#b3b3b3") >> cloud_nat

    # Infra
    terraform >> Edge(label="provision", style="dashed", color="#7b8cde") >> cluster_node

    # Autoscaling/HA
    hpa_fe >> Edge(label="scales", style="dashed", color="#888") >> fe_pod
    hpa_mw >> Edge(label="scales", style="dashed", color="#888") >> mw_pod
    hpa_kserve >> Edge(label="scales", style="dashed", color="#888") >> kserve_pod

    # KEDA
    kafka >> Edge(label="scale on lag", style="dashed", color="#888") >> keda
    keda >> Edge(label="scales", style="dashed", color="#888") >> be_pod