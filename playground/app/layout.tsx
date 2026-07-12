import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// privacyshield's frontend uses Inter as its body font — matching it here
// per the owner's explicit "borrow the template from privacyshield" UAT
// feedback (2026-07-12), replacing the create-next-app Geist default.
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Job Matcher Playground",
  description: "Resume + job links in, evidence-grounded fit reports out.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
