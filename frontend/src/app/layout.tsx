import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Constraint AI",
  description: "Engineering constraint graph visualization tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
