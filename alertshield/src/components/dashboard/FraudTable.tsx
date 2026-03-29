import { motion } from "framer-motion";
export interface TableFraudCase {
  id: string;
  employee: string;
  department: string;
  emailId: string;
  fraudStatus: "Phishing" | "Investigation" | "Legitimate";
  systemDecision: string;
  humanVerification: string;
  explanation?: string;
  timestamp: string;
}

interface FraudTableProps {
  cases: TableFraudCase[];
  onVerify?: (id: string, status: string) => void;
}

const FraudTable = ({ cases, onVerify }: FraudTableProps) => {
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.6 }}
      className="glass-card p-5 overflow-x-auto"
    >
      <h3 className="text-sm font-semibold text-foreground mb-4">Recent Fraud Cases</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            {["Employee", "Department", "Email ID", "Fraud Status", "System Decision", "Human Verification", "Timestamp"].map((h) => (
              <th key={h} className="text-left py-3 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cases.map((c, i) => (
            <tr key={i} className="border-b border-border/50 transition-colors hover:bg-muted/30">
              <td className="py-3 px-3 font-medium text-foreground">{c.employee}</td>
              <td className="py-3 px-3 text-muted-foreground">{c.department}</td>
              <td className="py-3 px-3 text-muted-foreground font-mono text-xs">{c.emailId}</td>
              <td className="py-3 px-3">
                <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-semibold ${
                  c.fraudStatus === "Phishing"
                    ? "bg-destructive/15 text-destructive"
                    : c.fraudStatus === "Investigation" ? "bg-warning/15 text-warning" : "bg-success/15 text-success"
                }`}>
                  {c.fraudStatus}
                </span>
                {c.explanation && (
                  <div className="group relative cursor-pointer text-[10px] text-muted-foreground mt-1.5 max-w-[200px]">
                    <div className="truncate group-hover:invisible transition-all">
                      {c.explanation.substring(0, 45)}{c.explanation.length > 45 ? '...' : ''}
                    </div>
                    <div className="absolute opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto z-50 bg-background/95 backdrop-blur-md border border-border p-3 rounded-lg shadow-2xl text-xs text-foreground w-[280px] -top-1 -left-1 transform scale-95 group-hover:scale-110 transition-all duration-300 origin-top-left">
                      <div className="font-semibold text-primary/80 mb-1 border-b border-border/50 pb-1">AI Reasoning</div>
                      {c.explanation}
                    </div>
                  </div>
                )}
              </td>
              <td className="py-3 px-3 text-muted-foreground">{c.systemDecision}</td>
              <td className="py-3 px-3 text-muted-foreground">
                <select 
                    value={c.humanVerification || "Pending"}
                    onChange={(e) => onVerify && onVerify(c.id, e.target.value)}
                    className="bg-transparent border border-border rounded px-2 py-1 text-xs focus:ring-1 focus:ring-primary"
                >
                    <option value="Pending">Pending</option>
                    <option value="Confirmed Fraud">Confirmed Fraud</option>
                    <option value="Confirmed Safe">Confirmed Safe</option>
                    <option value="False Positive">False Positive</option>
                    <option value="False Negative">False Negative</option>
                </select>
              </td>
              <td className="py-3 px-3 text-muted-foreground">{c.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
};

export default FraudTable;
