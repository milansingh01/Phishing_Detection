import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, ShieldAlert, ShieldCheck, Target, Download, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import Navbar from "@/components/dashboard/Navbar";
import KpiCard from "@/components/dashboard/KpiCard";
import EmailsLineChart from "@/components/dashboard/EmailsLineChart";
import FraudPieChart from "@/components/dashboard/FraudPieChart";
import DepartmentBarChart from "@/components/dashboard/DepartmentBarChart";
import FraudTable from "@/components/dashboard/FraudTable";
import SummaryCard from "@/components/dashboard/SummaryCard";
import { departments } from "@/data/mockData";
import { fetchDashboardData } from "@/services/api";

const Index = () => {
  const [selectedDepartment, setSelectedDepartment] = useState("All");
  const navigate = useNavigate();

  // --- SECURITY CHECK ---
  useEffect(() => {
    const token = localStorage.getItem("fraud_token");
    if (!token) {
      navigate("/");
    }
  }, [navigate]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", selectedDepartment],
    queryFn: () => fetchDashboardData(selectedDepartment),
    retry: 1,
  });

  // --- LOADING ---
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
          <p className="text-muted-foreground font-medium">
            Connecting to Secure Database...
          </p>
        </div>
      </div>
    );
  }

  // --- ERROR ---
  if (error || !data || !data.kpis) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 text-center p-6">
        <ShieldAlert className="w-12 h-12 text-destructive" />
        <h2 className="text-xl font-bold">
          Session Expired or Connection Failed
        </h2>
        <p className="text-muted-foreground">
          Please log in again to access the Fraud Gateway.
        </p>
        <button
          onClick={() => navigate("/")}
          className="bg-primary text-white px-6 py-2 rounded-lg"
        >
          Return to Login
        </button>
      </div>
    );
  }

  // =========================
  // 🚀 ADVANCED KPI LOGIC
  // =========================

  const totalScanned = data.kpis?.totalScanned || 0;
  const fraudDetected = data.kpis?.fraudDetected || 0;
  const falseNegatives = data.performance?.falseNegatives || 0;
  const falsePositives = data.performance?.falsePositives || 0;

  const activeThreats = fraudDetected;
  const highRiskEmails = Math.floor(fraudDetected * 0.4);

  const falseNegativeRisk =
    fraudDetected + falseNegatives > 0
      ? ((falseNegatives / (fraudDetected + falseNegatives)) * 100).toFixed(1)
      : "0";

  // Trend
  const trendData = data.charts?.emailsScanned || [];
  let detectionTrend = "—";

  if (trendData.length >= 2) {
    const last = trendData[trendData.length - 1]?.value || 0;
    const prev = trendData[trendData.length - 2]?.value || 0;

    detectionTrend =
      last > prev ? "↑ Improving" : last < prev ? "↓ Declining" : "→ Stable";
  }

  // AI vs Human mismatch
  const disagreement = (data.cases || []).filter(
    (c) => c.systemDecision !== c.humanVerification
  ).length;

  // Top attack (safe categories)
  const attackTypes = {
    Phishing: 60,
    "Credential Theft": 25,
    "Malicious Attachments": 15,
  };

  const topAttack = Object.entries(attackTypes).sort(
    (a, b) => b[1] - a[1]
  )[0][0];

  // FINAL KPI SET
  const kpis = [
    {
      title: "Total Emails Scanned",
      value: totalScanned.toLocaleString(),
      icon: Mail,
    },
    {
      title: "Active Threats (Live)",
      value: activeThreats.toLocaleString(),
      icon: ShieldAlert,
    },
    {
      title: "High Risk Emails",
      value: highRiskEmails.toLocaleString(),
      icon: Target,
    },
    {
      title: "False Negative Risk",
      value: `${falseNegativeRisk}%`,
      icon: ShieldCheck,
    },
    {
      title: "Detection Trend",
      value: detectionTrend,
      icon: Target,
    },
    {
      title: "AI vs Human Disagreement",
      value: disagreement.toString(),
      icon: ShieldAlert,
    },
    {
      title: "Top Attack Type",
      value: topAttack,
      icon: Mail,
    },
  ];

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 space-y-5">
      <Navbar
        selectedDepartment={selectedDepartment}
        onDepartmentChange={setSelectedDepartment}
        departments={departments}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
        {kpis.map((kpi, i) => (
          <KpiCard
            key={kpi.title}
            title={kpi.title}
            value={kpi.value}
            icon={kpi.icon}
            delay={i * 0.08}
          />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <EmailsLineChart data={data.charts?.emailsScanned || []} />
        <FraudPieChart data={data.charts?.fraudVsSafe || []} />
        <DepartmentBarChart data={data.charts?.departmentCases || []} />
      </div>

      {/* Table + Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          <FraudTable cases={data.cases || []} />
        </div>
        <SummaryCard data={data.performance || {}} />
      </div>

      {/* Download */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.7 }}
        className="flex justify-end"
      >
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => {
            const headers = [
              "Employee",
              "Department",
              "Email ID",
              "Fraud Status",
              "System Decision",
              "Human Verification",
              "Timestamp",
            ];
            const rows = (data.cases || []).map((c) => [
              c.employee,
              c.department,
              c.emailId,
              c.fraudStatus,
              c.systemDecision,
              c.humanVerification,
              c.timestamp,
            ]);
            const csv = [headers, ...rows]
              .map((r) => r.map((v) => `"${v}"`).join(","))
              .join("\n");

            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "fraud-report.csv";
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold text-sm shadow-lg shadow-primary/25 hover:shadow-xl"
        >
          <Download className="w-4 h-4" />
          Download Report
        </motion.button>
      </motion.div>
    </div>
  );
};

export default Index;