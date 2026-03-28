export interface BackendCase {
  id: string;
  subject: string;
  sender: string;
  date: string;
  status: string;
  score: number;
  department: string;
  humanVerification: string;
  explanation: string;
}

export interface DashboardResponse {
  kpis: {
    totalScanned: number;
    fraudDetected: number;
    safeEmails: number;
    accuracy: number;
    moneySaved: number;
  };
  charts: {
    emailsScanned: { date: string; emails: number }[];
    fraudVsSafe: { name: string; value: number; color: string }[];
    departmentCases: { department: string; cases: number }[];
  };
  cases: BackendCase[];
  performance: {
    accuracy: number;
    falsePositives: number;
    falseNegatives: number;
  };
}

// Simulate network delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const fetchDashboardData = async (department: string): Promise<DashboardResponse> => {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://127.0.0.1:8000/api/dashboard?department=${encodeURIComponent(department)}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.status === 401) {
       localStorage.removeItem("token");
       window.location.href = "/login";
       throw new Error("Unauthorized");
    }

    if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Dashboard backend fetch failed, using fallback/error handling", error);
    // Returning empty structure on failure so UI doesn't completely crash immediately
    return {
      kpis: { totalScanned: 0, fraudDetected: 0, safeEmails: 0, accuracy: 0, moneySaved: 0 },
      charts: { emailsScanned: [], fraudVsSafe: [], departmentCases: [] },
      cases: [],
      performance: { accuracy: 0, falsePositives: 0, falseNegatives: 0 },
    };
  }
};

export const updateVerificationStatus = async (caseId: string, status: string): Promise<boolean> => {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://127.0.0.1:8000/api/dashboard/cases/${caseId}/verify`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status })
    });
    return response.ok;
  } catch (err) {
    console.error("Failed to update verification", err);
    return false;
  }
};
