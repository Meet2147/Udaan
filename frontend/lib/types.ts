export type Tokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type User = {
  id: number;
  role: 'admin' | 'student' | 'super_admin';
  full_name: string;
  email: string;
  phone: string;
  grade_or_standard: string;
};
