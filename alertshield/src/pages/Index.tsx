import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Mail, ShieldAlert, ShieldCheck, Target, AlertTriangle, Activity, BrainCircuit, Download } from "lucide-react";
import Navbar from "@/components/dashboard/Navbar";
import KpiCard from "@/components/dashboard/KpiCard";
import EmailsLineChart from "@/components/dashboard/EmailsLineChart";
import FraudPieChart from "@/components/dashboard/FraudPieChart";
import DepartmentBarChart from "@/components/dashboard/DepartmentBarChart";
import FraudTable from "@/components/dashboard/FraudTable";
import SummaryCard from "@/components/dashboard/SummaryCard";
import { departments } from "@/data/mockData";
import { fetchDashboardData, DashboardResponse } from "@/services/api";

const Index = () => {
  const [selectedDepartment, setSelectedDepartment] = useState("All");
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const result = await fetchDashboardData(selectedDepartment);
        setData(result);
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    // Quick polling every 5 seconds to simulate real-time dashboard updates from kafka
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [selectedDepartment]);

  if (loading && !data) return <div className="p-8 text-center bg-background text-white min-h-screen">Loading live data...</div>;
  if (!data) return <div className="p-8 text-center text-red-500 min-h-screen bg-background">Critical Error: Database connection failed.</div>;

  // ✅ MAPPED CASES
  const casesMapped = data?.cases.map(c => ({
    employee: c.sender === "Unknown Extracted" ? "unknown@external.com" : c.sender,
    department: c.department,
    emailId: c.sender === "Unknown Extracted" ? "unknown@external.com" : c.sender,
    fraudStatus: c.status as "Phishing" | "Legitimate" | "Investigation",
    systemDecision: c.status,
    humanVerification: c.humanVerification,
    explanation: c.explanation,
    timestamp: new Date(c.date).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }),
  })) || [];

  const handleVerify = async (id: string, status: string) => {
      // Optimistic update omitted, we just await and reload
      const success = await import("@/services/api").then(m => m.updateVerificationStatus(id, status));
      if (success) {
          const result = await fetchDashboardData(selectedDepartment);
          setData(result);
      }
  };

  // ✅ NEW KPI STRUCTURE
  const kpis = [
    { title: "Active Threats (Live)", value: data?.kpis.fraudDetected || 0, icon: AlertTriangle },
    { title: "High Risk Emails (Priority Queue)", value: data?.kpis.fraudDetected || 0, icon: ShieldAlert },
    { title: "False Negative Risk", value: `${(100 - (data?.kpis.accuracy || 100)).toFixed(1)}%`, icon: Target },
    { title: "Detection Trend", value: "Improving", icon: Activity },
    { title: "Total Scanned", value: data?.kpis.totalScanned || 0, icon: BrainCircuit },
    { title: "Safe Scanned", value: data?.kpis.safeEmails || 0, icon: Mail },
  ];

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 space-y-5">

      <Navbar
        selectedDepartment={selectedDepartment}
        onDepartmentChange={setSelectedDepartment}
        departments={departments}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-4">
        {kpis.map((kpi, i) => (
          <KpiCard
            key={kpi.title}
            title={kpi.title}
            value={String(kpi.value)}
            icon={kpi.icon}
            delay={i * 0.08}
          />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <EmailsLineChart data={data.charts.emailsScanned} />
        <FraudPieChart data={data.charts.fraudVsSafe} />
        <DepartmentBarChart data={data.charts.departmentCases} />
      </div>

      {/* Table + Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          <FraudTable cases={casesMapped} onVerify={handleVerify} />
        </div>
        <SummaryCard data={data.performance} />
      </div>

      {/* Download Button */}
      <motion.div className="flex justify-end">
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => {
            const headers = ["Employee", "Department", "Email ID", "Fraud Status", "System Decision", "Human Verification", "Timestamp"];
            const rows = casesMapped.map(c => [c.employee, c.department, c.emailId, c.fraudStatus, c.systemDecision, c.humanVerification, c.timestamp]);
            const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(",")).join("\n");
            const blob = new Blob([csv], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "fraud-report.csv";
            a.click();
            URL.revokeObjectURL(url);
          }}
          className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold text-sm"
        >
          <Download className="w-4 h-4" />
          Download Report
        </motion.button>
      </motion.div>
    </div>
  );
};

export default Index;