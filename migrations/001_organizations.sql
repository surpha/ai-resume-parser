-- ════════════════════════════════════════════════════════════════════════
-- Resume Scan AI — Organization & Profile Schema
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ════════════════════════════════════════════════════════════════════════

-- 1. Organizations table
--    status: pending (awaiting platform admin approval) → active → suspended
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    invite_code TEXT UNIQUE DEFAULT substr(md5(random()::text), 1, 8),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'suspended')),
    created_by UUID REFERENCES auth.users(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Profiles table (extends auth.users)
--    Roles:
--      platform_admin  — you (approves orgs)
--      company_admin   — org creator (approves members, manages org)
--      member          — approved team member
--      pending_member  — joined via invite code, awaiting company_admin approval
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    role TEXT DEFAULT 'pending_member' CHECK (role IN ('platform_admin', 'company_admin', 'member', 'pending_member')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Add org_id to existing tables for multi-tenancy
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id);

-- 4. Indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_org ON profiles(org_id);
CREATE INDEX IF NOT EXISTS idx_candidates_org ON candidates(org_id);
CREATE INDEX IF NOT EXISTS idx_jobs_org ON jobs(org_id);
CREATE INDEX IF NOT EXISTS idx_analyses_org ON analyses(org_id);

-- 5. Helper function to get user's org_id (bypasses RLS to avoid recursion)
CREATE OR REPLACE FUNCTION get_user_org_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT org_id FROM profiles WHERE id = auth.uid();
$$;

-- 6. RLS policies
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Organizations: users can see their own org
DROP POLICY IF EXISTS "Users can view own org" ON organizations;
CREATE POLICY "Users can view own org"
    ON organizations FOR SELECT
    USING (id = get_user_org_id());

DROP POLICY IF EXISTS "Authenticated users can create orgs" ON organizations;
CREATE POLICY "Authenticated users can create orgs"
    ON organizations FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- Profiles: user can see own profile + org members
DROP POLICY IF EXISTS "Users can view org members" ON profiles;
CREATE POLICY "Users can view org members"
    ON profiles FOR SELECT
    USING (id = auth.uid() OR org_id = get_user_org_id());

DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (id = auth.uid());

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (id = auth.uid());

-- Candidates: org-scoped
DROP POLICY IF EXISTS "Org members can view candidates" ON candidates;
CREATE POLICY "Org members can view candidates"
    ON candidates FOR SELECT
    USING (org_id = get_user_org_id());

DROP POLICY IF EXISTS "Org members can insert candidates" ON candidates;
CREATE POLICY "Org members can insert candidates"
    ON candidates FOR INSERT
    WITH CHECK (org_id = get_user_org_id());

DROP POLICY IF EXISTS "Org members can delete candidates" ON candidates;
CREATE POLICY "Org members can delete candidates"
    ON candidates FOR DELETE
    USING (org_id = get_user_org_id());

-- Jobs: org-scoped
DROP POLICY IF EXISTS "Org members can view jobs" ON jobs;
CREATE POLICY "Org members can view jobs"
    ON jobs FOR SELECT
    USING (org_id = get_user_org_id());

DROP POLICY IF EXISTS "Org members can insert jobs" ON jobs;
CREATE POLICY "Org members can insert jobs"
    ON jobs FOR INSERT
    WITH CHECK (org_id = get_user_org_id());

DROP POLICY IF EXISTS "Org members can delete jobs" ON jobs;
CREATE POLICY "Org members can delete jobs"
    ON jobs FOR DELETE
    USING (org_id = get_user_org_id());

-- Analyses: org-scoped
DROP POLICY IF EXISTS "Org members can view analyses" ON analyses;
CREATE POLICY "Org members can view analyses"
    ON analyses FOR SELECT
    USING (org_id = get_user_org_id());

DROP POLICY IF EXISTS "Org members can insert analyses" ON analyses;
CREATE POLICY "Org members can insert analyses"
    ON analyses FOR INSERT
    WITH CHECK (org_id = get_user_org_id());

-- 7. Grant access to all roles
GRANT ALL ON organizations TO anon, authenticated, service_role;
GRANT ALL ON profiles TO anon, authenticated, service_role;
GRANT ALL ON candidates TO anon, authenticated, service_role;
GRANT ALL ON jobs TO anon, authenticated, service_role;
GRANT ALL ON analyses TO anon, authenticated, service_role;
