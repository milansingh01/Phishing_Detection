import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface FraudPieChartProps {
  data: { name: string; value: number; color: string }[];
}

const FraudPieChart = ({ data }: FraudPieChartProps) => {
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="glass-card p-5"
    >
      <h3 className="text-sm font-semibold text-foreground mb-4">Fraud vs Safe Emails</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={45}
            outerRadius={70}
            dataKey="value"
            stroke="none"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: "hsl(0, 0%, 100%)", border: "1px solid hsl(210, 15%, 88%)", borderRadius: "0.75rem", color: "hsl(215, 25%, 15%)" }}
            formatter={(value: number, name: string, props: any) => [`${value} Scans ${(props?.payload?.percent ? '(' + (props.payload.percent * 100).toFixed(1) + '%)' : '')}`, name]}
          />
        </PieChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default FraudPieChart;
