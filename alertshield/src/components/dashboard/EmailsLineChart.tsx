import { useState } from "react";
import { motion } from "framer-motion";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

interface EmailsLineChartProps {
  data: { date: string; emails: number }[];
}

const EmailsLineChart = ({ data }: EmailsLineChartProps) => {
  const [range, setRange] = useState("30");
  const filteredData = data.slice(-Number(range));

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="glass-card p-5"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-foreground">Emails Scanned – Focus View</h3>
        <select 
          className="bg-transparent border border-border text-xs rounded-md px-2 py-1 outline-none text-muted-foreground focus:ring-1 focus:ring-primary"
          value={range}
          onChange={(e) => setRange(e.target.value)}
        >
          <option value="1">Today</option>
          <option value="5">Last 5 Days</option>
          <option value="30">Last 30 Days</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={filteredData}>
          <defs>
            <linearGradient id="emailGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(197, 100%, 47%)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="hsl(197, 100%, 47%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(210, 15%, 90%)" />
          <XAxis dataKey="date" tick={{ fill: "hsl(215, 15%, 50%)", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "hsl(215, 15%, 50%)", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: "hsl(0, 0%, 100%)", border: "1px solid hsl(210, 15%, 88%)", borderRadius: "0.75rem", color: "hsl(215, 25%, 15%)" }}
          />
          <Area type="monotone" dataKey="emails" stroke="hsl(197, 100%, 47%)" fill="url(#emailGradient)" strokeWidth={2} dot={{ r: 3, fill: "hsl(197, 100%, 47%)" }} />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default EmailsLineChart;
