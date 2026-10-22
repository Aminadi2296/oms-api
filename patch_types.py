path = r'c:\Projects\oms\src\types\client.ts'
with open(path, 'w', encoding='utf-8') as f:
    f.write('''export type Client = {
  id: number
  
  // B2B Customer Fields
  razon_social?: string
  nombre_comercial?: string | null
  tipo_documento?: string | null
  numero_fiscal?: string | null
  regimen_fiscal?: string | null
  region?: string | null
  ciudad?: string | null
  codigo_postal?: string | null
  direccion_fiscal?: string | null
  direccion_despacho?: string | null
  telefono_principal?: string | null
  correo_principal?: string | null
  sitio_web?: string | null
  contacto_nombre?: string | null
  contacto_cargo?: string | null
  contacto_telefono?: string | null
  contacto_correo?: string | null
  condicion_pago?: string | null
  limite_credito?: number | null
  moneda?: string | null
  notas?: string | null
  estatus?: string | null

  // Legacy Fields (Optional for backward compatibility)
  first_name?: string
  last_name?: string
  document_number?: string
  client_type?: string
  is_member_of_group?: boolean
  person_type?: 'N' | 'J' | string
  source?: 'C' | 'P'
  birth_place?: string
  birth_date?: string
  join_date?: string
  email_1?: string
  mobile_1?: string
  email_2?: string | null
  mobile_2?: string | null
  phone?: string | null
  reference?: string | null
  doc?: string
  billing_address?: string | null
  client_category_id?: number
  office_id?: number
  agent_id?: number | null
  executive_id?: number | null
  client_group_id?: number | null
  client_branch_id?: number
  city_id?: number | null
  zone_id?: number | null

  personal_data?: {
    gender?: string | null
    civil_status?: string | null
    height?: number | null
    weight?: number | null
    smoker?: boolean | null
    sports?: string | null
    rif?: string | null
    profession_id?: number | null
    occupation_id?: number | null
    monthly_income?: number | null
    pathology?: string | null
  }

  legal_data?: {
    legal_representative?: string | null
    economic_activity_id?: number | null
  }

  documents?: {
    type: string
    expiration_date: string
    status: string
    due: boolean
  }[]

  bank_accounts?: {
    bank_name: string
    account_number: string
    currency: string
    account_type: string
    notes?: string | null
  }[]

  contacts?: {
    full_name: string
    position: string
    phone: string
    email: string
    notes?: string | null
  }[]

  created_at?: string
  updated_at?: string
}
''')
print("TYPES UPDATED")
