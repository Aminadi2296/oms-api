import re

path = r'c:\Projects\oms\src\app\(dashboard)\clients\page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace formatFullName
old_format = """const formatFullName = (client: Client) =>
  client.client_type === 'J' ? client?.last_name : `${client.first_name || ''} ${client.last_name || ''}`.trim()"""

new_format = """const formatFullName = (client: Client) => {
  if (client?.razon_social) {
    return client.nombre_comercial
      ? `${client.razon_social} (${client.nombre_comercial})`
      : client.razon_social
  }
  if (client?.client_type === 'J') return client?.last_name || 'Sin nombre'
  return `${client?.first_name || ''} ${client?.last_name || ''}`.trim() || 'Sin nombre'
}"""

if old_format in content:
    content = content.replace(old_format, new_format)
    print("FORMAT_FULL_NAME: REPLACED")
else:
    print("FORMAT_FULL_NAME: NOT FOUND")

# Replace columns definition
old_columns = """      {
        key: 'document' as const,
        label: 'Documento',
        render: (_: any, client: Client) => (
          <Box>
            {client?.client_type}-{client?.document_number}
          </Box>
        )
      },
      {
        key: 'client' as const,
        label: 'Cliente',
        render: (_: any, client: Client) => (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              width: '250px',
              minWidth: '250px'
            }}
          >
            <Tooltip title={formatFullName(client)} placement='top-start' arrow>
              <Typography
                variant='body2'
                sx={{
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  maxWidth: '100%'
                }}
              >
                {formatFullName(client)}
              </Typography>
            </Tooltip>

            <Typography
              variant='caption'
              sx={{
                fontSize: '0.8em',
                color: '#666',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '100%'
              }}
            >
              {client.email_1 || 'Sin correo'}
            </Typography>
          </Box>
        )
      },
      {
        key: 'type' as const,
        label: 'Tipo',
        render: (_: any, client: Client) => client?.person_type || ''
      },
      {
        key: 'birth_date' as const,
        label: 'Fecha Nac./Fund.',
        render: (date: string) => (date ? new Date(date).toLocaleDateString() : 'N/A')
      },"""

new_columns = """      {
        key: 'document' as const,
        label: 'Documento / Fiscal',
        render: (_: any, client: Client) => (
          <Box>
            {client?.numero_fiscal || (client?.document_number ? `${client?.client_type || ''}-${client.document_number}` : 'N/A')}
          </Box>
        )
      },
      {
        key: 'client' as const,
        label: 'Cliente / Empresa',
        render: (_: any, client: Client) => (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              width: '250px',
              minWidth: '250px'
            }}
          >
            <Tooltip title={formatFullName(client)} placement='top-start' arrow>
              <Typography
                variant='body2'
                sx={{
                  fontWeight: 500,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  maxWidth: '100%'
                }}
              >
                {formatFullName(client)}
              </Typography>
            </Tooltip>

            <Typography
              variant='caption'
              sx={{
                fontSize: '0.8em',
                color: '#666',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '100%'
              }}
            >
              {client.correo_principal || client.email_1 || 'Sin correo'}
            </Typography>
          </Box>
        )
      },
      {
        key: 'phone' as const,
        label: 'Teléfono',
        render: (_: any, client: Client) => (
          <Typography variant='body2'>
            {client?.telefono_principal || client?.mobile_1 || 'N/A'}
          </Typography>
        )
      },
      {
        key: 'status' as const,
        label: 'Estado',
        render: (_: any, client: Client) => (
          <Typography
            variant='caption'
            sx={{
              px: 1.5,
              py: 0.5,
              borderRadius: 1,
              bgcolor: (client?.estatus || 'Activo').toLowerCase() === 'activo' ? 'success.light' : 'grey.300',
              color: (client?.estatus || 'Activo').toLowerCase() === 'activo' ? 'success.dark' : 'text.secondary',
              fontWeight: 600
            }}
          >
            {client?.estatus || 'Activo'}
          </Typography>
        )
      },"""

if old_columns in content:
    content = content.replace(old_columns, new_columns)
    print("COLUMNS: REPLACED")
else:
    print("COLUMNS: NOT FOUND")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("CLIENTS PAGE UPDATED")
