import { apiRequest, asObject, withFields } from "./api";

export type InquiryInput = {
  name: string;
  mobile: string;
  email?: string;
  message: string;
  service?: string;
  language?: string;
};

export type InquiryResult = {
  id: number;
  name: string;
  mobile: string;
  language: string;
  status: string;
  created_at: string;
};

export function submitInquiry(input: InquiryInput) {
  return apiRequest("/contact-inquiries/", (v, e) => {
    const r = asObject(v, e);
    withFields(r, e, ["id", "name"]);
    return r as unknown as InquiryResult;
  }, { method: "POST", body: input });
}
