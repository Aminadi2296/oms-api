path = r'c:\Projects\oms\src\app\(dashboard)\clients\create\page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
old_import = "import { useSnackbar } from '@/hooks/useSnackbar'"
new_import = "import { useSnackbar } from '@/hooks/useSnackbar'\nimport { useApi } from '@/hooks/useApi'"

if old_import in content:
    content = content.replace(old_import, new_import)
    print("IMPORT: ADDED")
else:
    print("IMPORT: NOT FOUND")

# 2. Add useApi hook call
old_hook = "  const { showSuccess, showError } = useSnackbar()"
new_hook = "  const { showSuccess, showError } = useSnackbar()\n  const { fetchApi } = useApi()"

if old_hook in content:
    content = content.replace(old_hook, new_hook)
    print("HOOK: ADDED")
else:
    print("HOOK: NOT FOUND")

# 3. Replace handleSubmit
old_submit = """  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      showSuccess('Cliente creado exitosamente!')
      setTimeout(() => {
        router.push(ROUTES.CLIENTS.INDEX)
      }, 1500)
    } catch (error: any) {
      showError('Error al crear el cliente')
    } finally {
      setIsSubmitting(false)
    }
  }"""

new_submit = """  const handleSubmit = async () => {
    if (!formData.razonSocial?.trim()) {
      showError('La Razón Social es requerida')
      setActiveStep(0)
      return
    }

    setIsSubmitting(true)

    try {
      await fetchApi('clients', {
        method: 'POST',
        body: formData
      })
      showSuccess('Cliente creado exitosamente!')
      setTimeout(() => {
        router.push(ROUTES.CLIENTS.INDEX)
      }, 1000)
    } catch (error: any) {
      showError(error?.message || 'Error al crear el cliente')
    } finally {
      setIsSubmitting(false)
    }
  }"""

if old_submit in content:
    content = content.replace(old_submit, new_submit)
    print("SUBMIT: REPLACED")
else:
    print("SUBMIT: NOT FOUND")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("CREATE PAGE UPDATED")
