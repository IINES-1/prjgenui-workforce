/* PRJGENUI Workforce — interface languages (English, Spanish, Portuguese).
 *
 * A dictionary-driven runtime translator. The interface was built in
 * English; this layer maps each known interface string to its Spanish
 * and Portuguese counterpart, applies it to the DOM (including content
 * the app renders later), and offers a language selector in the top
 * bar. The choice is remembered per browser. User-entered data (names,
 * trades, notes) is never translated — only fixed interface wording.
 *
 * Strings that are not in the dictionary simply remain in English, so a
 * missing entry degrades gracefully. Dates translate their month names
 * via a pattern rule so "26 Oct 2026" becomes "26 out 2026" in
 * Portuguese and so on.
 */
(function () {
  'use strict';

  var ES = {
    /* sign-in and access */
    'Sign in': 'Iniciar sesión',
    'For the PRJGENUI team, contractors and registered workers.': 'Para el equipo de PRJGENUI, contratistas y trabajadores registrados.',
    'Email': 'Correo electrónico',
    'Password': 'Contraseña',
    'Forgot your password?': '¿Olvidó su contraseña?',
    'Have an invitation code?': '¿Tiene un código de invitación?',
    'Set up your access': 'Configure su acceso',
    'Enter your invitation details and choose a password.': 'Introduzca los datos de su invitación y elija una contraseña.',
    'Choose a password': 'Elija una contraseña',
    'Invitation code': 'Código de invitación',
    'Create my account': 'Crear mi cuenta',
    'You will receive an email to confirm your address. After confirming, sign in here and your access finishes setting up on its own.': 'Recibirá un correo electrónico para confirmar su dirección. Después de confirmar, inicie sesión aquí y su acceso terminará de configurarse solo.',
    'Back to sign in': 'Volver a iniciar sesión',
    'Access is by invitation only. If you cannot sign in, write to hello@prjgenuiworkforce.co.uk.': 'El acceso es solo por invitación. Si no puede iniciar sesión, escriba a hello@prjgenuiworkforce.co.uk.',
    '— we will email you a link to set a new one.': '— le enviaremos por correo electrónico un enlace para establecer una nueva.',
    'Welcome': 'Bienvenido',
    'Sign out': 'Cerrar sesión',
    'Loading your profile…': 'Cargando su perfil…',
    'Loading…': 'Cargando…',
    'Your account is not linked yet': 'Su cuenta aún no está vinculada',
    'Your sign-in works, but no role has been assigned to it. If you have an invitation code, enter it below to finish setting up.': 'Su inicio de sesión funciona, pero no se le ha asignado ningún rol. Si tiene un código de invitación, introdúzcalo a continuación para terminar la configuración.',
    'Finish setup': 'Terminar configuración',

    /* two-factor */
    'Set up two-factor': 'Configurar la verificación en dos pasos',
    'Two-factor verification': 'Verificación en dos pasos',
    'Enter the 6-digit code from your authenticator app.': 'Introduzca el código de 6 dígitos de su aplicación de autenticación.',
    'Admin accounts need an authenticator app (Google Authenticator, Microsoft Authenticator or similar). Scan the code with the app, then enter the 6-digit code it shows.': 'Las cuentas de administración necesitan una aplicación de autenticación (Google Authenticator, Microsoft Authenticator o similar). Escanee el código con la aplicación e introduzca el código de 6 dígitos que muestra.',
    'Or enter this code manually in your app:': 'O introduzca este código manualmente en su aplicación:',
    '6-digit code': 'Código de 6 dígitos',
    'Verify': 'Verificar',
    'Use a different account': 'Usar otra cuenta',

    /* header and dashboard */
    'Team platform': 'Plataforma del equipo',
    'Compliance Action Centre': 'Centro de acciones de cumplimiento',
    'Run reminders': 'Ejecutar recordatorios',
    'Recompute schedule': 'Recalcular el calendario',
    'Workers': 'Trabajadores',
    'Crews': 'Equipos',
    'Workforce requests': 'Solicitudes de personal',
    'Assignments': 'Asignaciones',
    'Attendance': 'Asistencia',
    'Replacement incidents': 'Incidentes de sustitución',
    'Invitations': 'Invitaciones',
    'Prices': 'Precios',

    /* roles */
    'Owner': 'Propietario',
    'Operations': 'Operaciones',
    'Compliance': 'Cumplimiento',
    'Contractor': 'Contratista',
    'Worker': 'Trabajador',
    'Supplier': 'Proveedor',
    'Auditor': 'Auditor',

    /* worker records */
    'Full name': 'Nombre completo',
    'Trade': 'Oficio',
    'Add worker': 'Añadir trabajador',
    'Passport': 'Pasaporte',
    'Name': 'Nombre',
    'Status': 'Estado',
    'Open': 'Abrir',
    'Close': 'Cerrar',
    'Advance status': 'Avanzar estado',
    'Reason (required to block or archive)': 'Motivo (obligatorio para bloquear o archivar)',
    'Reason (recorded permanently)': 'Motivo (registrado permanentemente)',
    'Block': 'Bloquear',
    'Archive': 'Archivar',
    'Invite to sign in': 'Invitar a iniciar sesión',
    'Run readiness check': 'Ejecutar comprobación de preparación',
    'Readiness': 'Preparación',
    'Overrides': 'Excepciones',
    'An override relaxes one requirement for this worker for a time. It never edits a check, and it is recorded permanently.': 'Una excepción relaja un requisito de este trabajador durante un tiempo. Nunca modifica una comprobación y queda registrada permanentemente.',
    'Requirement': 'Requisito',
    'Approve override': 'Aprobar excepción',
    'Expires': 'Caduca',
    'Documents': 'Documentos',
    'Identity documents are restricted. Only the Owner and Compliance can open them.': 'Los documentos de identidad están restringidos. Solo el Propietario y Cumplimiento pueden abrirlos.',
    'Right to Work checks': 'Comprobaciones de derecho a trabajar',
    'Right to Work': 'Derecho a trabajar',
    'Method': 'Método',
    'Home Office share code': 'Código compartido del Home Office',
    'Manual passport check': 'Comprobación manual del pasaporte',
    'Check date': 'Fecha de comprobación',
    'Result': 'Resultado',
    'Pass': 'Aprobado',
    'Fail': 'No aprobado',
    'Follow-up required': 'Requiere seguimiento',
    'Follow-up due': 'Seguimiento pendiente el',
    'Source': 'Origen',
    'Record check': 'Registrar comprobación',
    'Cards and training': 'Tarjetas y formación',
    'Category': 'Categoría',
    'Card or qualification': 'Tarjeta o cualificación',
    'Training': 'Formación',
    'Type': 'Tipo',
    'Number (cards)': 'Número (tarjetas)',
    'Expiry': 'Caducidad',
    'Valid until': 'Válido hasta',
    'Expires on that date': 'Caduca en esa fecha',
    'Renewable — renews before it': 'Renovable — se renueva antes',
    'Permanent — no expiry': 'Permanente — sin caducidad',
    'Add': 'Añadir',
    'My passport': 'Mi pasaporte',
    'Cards, qualifications and training': 'Tarjetas, cualificaciones y formación',
    'Skill evidence and work history': 'Evidencias de habilidades e historial de trabajo',
    'My attendance': 'Mi asistencia',
    'If a record is wrong, dispute it — the team must review it before it changes, and the original stays on record either way.': 'Si un registro es incorrecto, discútalo — el equipo debe revisarlo antes de que cambie, y el original queda registrado en cualquier caso.',
    'Assignment': 'Asignación',
    'Date': 'Fecha',
    'Outcome': 'Resultado',
    'Performance': 'Rendimiento',
    'Reminders': 'Recordatorios',
    'My details': 'Mis datos',
    'Corrections go to the team straight away. Your name, passport number and status can only be changed by the team.': 'Las correcciones se envían al equipo de inmediato. Su nombre, número de pasaporte y estado solo puede cambiarlos el equipo.',
    'Phone': 'Teléfono',
    'Availability': 'Disponibilidad',
    'Save corrections': 'Guardar correcciones',
    'My documents': 'Mis documentos',
    'Replacement evidence': 'Evidencia de sustitución',
    'Passport or ID': 'Pasaporte o documento de identidad',
    'Certificate': 'Certificado',
    'Other': 'Otro',
    'File': 'Archivo',
    'Upload': 'Subir',
    'CSCS card': 'Tarjeta CSCS',
    'Worker record': 'Registro del trabajador',
    'Worker record not verified': 'Registro del trabajador no verificado',
    'Right to Work check missing': 'Falta la comprobación de derecho a trabajar',
    'Right to Work check did not pass': 'La comprobación de derecho a trabajar no fue aprobada',
    'Right to Work follow-up overdue': 'Seguimiento del derecho a trabajar vencido',

    /* worker statuses */
    'Draft': 'Borrador',
    'In review': 'En revisión',
    'Verified': 'Verificado',
    'Expiring soon': 'Caduca pronto',
    'Blocked': 'Bloqueado',
    'Archived': 'Archivado',
    'Pending review': 'Pendiente de revisión',
    'Rejected': 'Rechazado',

    /* crews */
    'A crew is a group of workers with a track record of working well together. A crew only exists once you have seen it happen.': 'Un equipo es un grupo de trabajadores con historial de trabajar bien juntos. Un equipo solo existe cuando lo ha visto funcionar.',
    'Add crew': 'Añadir equipo',
    'Crew': 'Equipo',
    'Members': 'Miembros',
    'Specialism': 'Especialidad',
    'Evidence': 'Evidencia',
    'Crew name': 'Nombre del equipo',
    'Supervisor': 'Supervisor',
    'None set': 'Sin establecer',
    'Ctrl/Cmd-click to select more than one.': 'Ctrl/Cmd-clic para seleccionar más de uno.',
    'Notes': 'Notas',
    'Deployment history': 'Historial de despliegues',
    'Log each time this crew went out together.': 'Registre cada vez que este equipo salió a trabajar.',
    'Client': 'Cliente',
    'Project': 'Proyecto',
    '+ Add deployment': '+ Añadir despliegue',
    'Delete crew': 'Eliminar equipo',
    'Cancel': 'Cancelar',
    'Save crew': 'Guardar equipo',

    /* requests and matching */
    'Add a contractor': 'Añadir un contratista',
    'Company name': 'Nombre de la empresa',
    'Contact name': 'Persona de contacto',
    'Add contractor': 'Añadir contratista',
    'Choose…': 'Elegir…',
    'Workers needed': 'Trabajadores necesarios',
    'Start date': 'Fecha de inicio',
    'Start': 'Inicio',
    'End': 'Fin',
    'Duration': 'Duración',
    'Create request': 'Crear solicitud',
    'Asbestos awareness': 'Concienciación sobre amianto',
    'Working at height': 'Trabajo en altura',
    'Manual handling': 'Manipulación manual de cargas',
    'Urgent': 'Urgente',
    'Ref': 'Ref',
    'Needed': 'Necesarios',
    'Matches': 'Coincidencias',
    'View matches': 'Ver coincidencias',
    'Run matching': 'Ejecutar emparejamiento',
    'Put forward': 'Propuesto',
    'Held back': 'Descartado',
    'Approve match': 'Aprobar coincidencia',
    'Send offer': 'Enviar oferta',
    'Factor': 'Factor',
    'Reason': 'Motivo',
    'Worker record is verified': 'El registro del trabajador está verificado',
    'Right to Work check is current': 'La comprobación de derecho a trabajar está vigente',
    'Trade matches the request': 'El oficio coincide con la solicitud',
    'Request': 'Solicitud',
    'Open': 'Abierta',

    /* request statuses */
    'Matched': 'Con coincidencias',
    'Offered': 'Oferta enviada',
    'Filled': 'Cubierta',
    'Closed': 'Cerrada',

    /* assignments lifecycle */
    'Proposed': 'Propuesta',
    'Accepted': 'Aceptada',
    'Confirmed': 'Confirmada',
    'Activate': 'Activar',
    'Active': 'Activa',
    'Completed': 'Completada',
    'Cancelled': 'Cancelada',
    'No show': 'No se presentó',
    'Replaced': 'Sustituida',
    'History': 'Historial',
    'Legacy': 'Histórica',
    'Accepted': 'Aceptada',
    'Accepted': 'Aceptada',
    'Declined': 'Rechazada',
    'Confirm': 'Confirmar',
    'Record outcome': 'Registrar resultado',
    'Worker attended': 'El trabajador asistió',
    'Yes': 'Sí',
    'No': 'No',
    'Rating': 'Valoración',
    '1 — poor': '1 — deficiente',
    '5 — excellent': '5 — excelente',
    'Would rehire': 'Se volvería a contratar',
    'Undecided': 'Sin decidir',
    'Client feedback': 'Comentarios del cliente',
    'Save outcome': 'Guardar resultado',
    'Back': 'Volver',
    'Assignment rates': 'Tarifas de la asignación',
    'Records only. Billing is built on top of these in a later stage.': 'Solo registros. La facturación se construirá sobre estas cifras en una fase posterior.',
    'Worker pay rate': 'Tarifa del trabajador',
    'Client charge rate': 'Tarifa cobrada al cliente',
    'Save rates': 'Guardar tarifas',
    'Statement': 'Extracto',
    'Rates': 'Tarifas',

    /* attendance */
    'One record per assignment and shift date. The existing record is the authoritative one — dispute it to correct it.': 'Un registro por asignación y fecha de turno. El registro existente es el autorizado — discútelo para corregirlo.',
    'Shift date': 'Fecha del turno',
    'Attended': 'Asistió',
    'Late': 'Con retraso',
    'Excused': 'Justificado',
    'Not recorded': 'Sin registrar',
    'Record attendance': 'Registrar asistencia',
    'Dispute': 'Disputar',
    'Resolve dispute': 'Resolver disputa',
    'Resolution': 'Resolución',
    'Original stands': 'El original se mantiene',
    'Corrected': 'Corregido',
    'Withdrawn by the worker': 'Retirado por el trabajador',
    'Corrected outcome (corrections only)': 'Resultado corregido (solo correcciones)',
    'Resolve': 'Resolver',
    'Recorded': 'Registrado',
    'Disputed': 'En disputa',

    /* replacement incidents */
    'Cancellation': 'Cancelación',
    'Replacement required': 'Sustitución necesaria',
    'Record incident': 'Registrar incidente',
    'Recorded': 'Registrado',
    'Replacement': 'Sustitución',
    'Incident': 'Incidente',
    'Record approval': 'Registrar aprobación',
    'Approved': 'Aprobado',
    'Refused': 'Rechazado',
    'Approval note': 'Nota de aprobación',
    'Add approval': 'Añadir aprobación',
    'Link replacement (same request, created through the offer flow)': 'Vincular sustitución (misma solicitud, creada mediante el flujo de oferta)',
    'Link': 'Vincular',
    'Acknowledge site pack': 'Confirmar recepción del paquete de sitio',
    'Resolve chain': 'Resolver cadena',

    /* invitations */
    'Create an invitation by email and role. Each one expires after seven days if unused.': 'Cree una invitación por correo y rol. Cada una caduca a los siete días si no se usa.',
    'Role': 'Rol',
    'Invite': 'Invitar',
    'Copy link': 'Copiar enlace',
    'Email invitee': 'Enviar correo al invitado',
    'Revoke': 'Revocar',
    'pending': 'pendiente',
    'Invitation emails are sent automatically once the invitation flow is connected in the next build step.': 'Los correos de invitación se envían automáticamente cuando el flujo de invitaciones se conecte en la siguiente fase.',

    /* prices, switches, costs */
    'Scope': 'Ámbito',
    'Standard': 'Estándar',
    'Customer-specific': 'Específico del cliente',
    'Contractor (customer prices)': 'Contratista (precios de cliente)',
    'Service': 'Servicio',
    'Managed onboarding': 'Incorporación gestionada',
    'Compliance monitoring': 'Supervisión de cumplimiento',
    'Training-request coordination': 'Coordinación de solicitudes de formación',
    'Right to Work check': 'Comprobación de derecho a trabajar',
    'Price (£)': 'Precio (£)',
    'Price': 'Precio',
    'Unit': 'Unidad',
    'VAT rate (%)': 'Tipo de IVA (%)',
    'Billing frequency': 'Frecuencia de facturación',
    'Minimum monthly (£)': 'Mínimo mensual (£)',
    'Discount (%)': 'Descuento (%)',
    'Discount reason (required with a discount)': 'Motivo del descuento (obligatorio con un descuento)',
    'Add price': 'Añadir precio',
    'Approval': 'Aprobación',
    'Service switches': 'Servicios activos',
    'Save switches': 'Guardar servicios',
    'Onboarding': 'Incorporación',
    'Monitoring': 'Supervisión',
    'Training': 'Formación',
    'From': 'Desde',
    'External costs': 'Costes externos',
    'Description': 'Descripción',
    'Training provider': 'Proveedor de formación',
    'Identity check': 'Comprobación de identidad',
    'Verification': 'Verificación',
    'Amount (£)': 'Importe (£)',
    'Amount': 'Importe',
    'Record cost': 'Registrar coste',
    'Your company': 'Su empresa',
    'Assignment statements': 'Extractos de asignación',
    'Generate new version': 'Generar nueva versión',
    'Assignment statement': 'Extracto de la asignación',

    /* footer */
    'PRJGENUI Workforce — internal platform. Not for public distribution.': 'PRJGENUI Workforce — plataforma interna. No para distribución pública.',

    /* a few common runtime messages */
    'That email and password did not match an account. Check both and try again.': 'Ese correo y contraseña no coinciden con ninguna cuenta. Compruebe ambos e inténtelo de nuevo.',
    'Enter the check date.': 'Introduzca la fecha de la comprobación.',
    'Configuration is missing, so sign-in is not available here.': 'Falta la configuración, por lo que el inicio de sesión no está disponible aquí.',
    'Record feedback': 'Registrar comentarios',
    'PRJGENUI Workforce — Team sign-in': 'PRJGENUI Workforce — Iniciar sesión',

    /* placeholders */
    '@e.g. painter and decorator': 'p. ej., pintor y decorador',
    '@e.g. Home Office online service': 'p. ej., servicio en línea del Home Office',
    '@e.g. cscs, ipaf, asbestos awareness': 'p. ej., cscs, ipaf, amianto',
    '@e.g. Painting crew A': 'p. ej., Equipo de pintura A',
    '@e.g. Education / occupied housing': 'p. ej., Educación / vivienda ocupada',
    '@e.g. Southwark Builds Ltd': 'p. ej., Construcciones Sur Ltd',
    '@e.g. 2 weeks': 'p. ej., 2 semanas',
    '@How the job went, from the client\x27s side': 'Cómo fue el trabajo, según el cliente',
    '@e.g. £180/day': 'p. ej., 180 £/día',
    '@e.g. £220/day': 'p. ej., 220 £/día',
    '@e.g. site log, supervisor call': 'p. ej., registro de sitio, llamada del supervisor',
    '@e.g. per worker per month': 'p. ej., por trabajador y mes',
    '@e.g. monthly': 'p. ej., mensual',

    /* ---- commercial and growth layer (migration 0026) ---- */

    /* control tower */
    'Control Tower': 'Torre de control',
    'Alerts': 'Alertas',
    'No alerts. Fill rate, margins, payments and compliance are all healthy.': 'Sin alertas. La tasa de cobertura, los márgenes, los pagos y el cumplimiento están sanos.',
    'Reports and exports': 'Informes y exportaciones',
    'Each button downloads a CSV of the current data — workers, assignments, approved timesheets (payroll-ready), invoices and attendance.': 'Cada botón descarga un CSV con los datos actuales: trabajadores, asignaciones, partes de horas aprobados (listos para nómina), facturas y asistencia.',
    'Timesheets (payroll)': 'Partes de horas (nómina)',
    'Invoices': 'Facturas',
    'Workers on file': 'Trabajadores registrados',
    'Verified workers': 'Trabajadores verificados',
    'Available now': 'Disponibles ahora',
    'Active contractors': 'Contratistas activos',
    'Open requests': 'Solicitudes abiertas',
    'Active assignments': 'Asignaciones activas',
    'Fill rate (30d)': 'Tasa de cobertura (30 d)',
    'Time to fill (30d)': 'Tiempo de cobertura (30 d)',
    'Attendance (30d)': 'Asistencia (30 d)',
    'No-shows (30d)': 'Ausencias (30 d)',
    'Open replacements': 'Sustituciones abiertas',
    'Expiring compliance': 'Cumplimiento por caducar',
    'Payment exposure': 'Exposición de pagos',
    'Overdue invoices': 'Facturas vencidas',
    'Approved revenue': 'Ingresos aprobados',
    'No overdue invoices.': 'No hay facturas vencidas.',

    /* workers: search, rates and availability */
    'Search workers': 'Buscar trabajadores',
    'Name, trade or passport number': 'Nombre, oficio o número de pasaporte',
    'Rates and availability': 'Tarifas y disponibilidad',
    'Default hourly rates are copied into new assignments. Travel range and base location feed capacity planning.': 'Las tarifas horarias predeterminadas se copian en las nuevas asignaciones. El radio de desplazamiento y la ubicación base alimentan la planificación de capacidad.',
    'Default pay (£/hour)': 'Pago predeterminado (£/hora)',
    'Overtime pay (£/hour)': 'Pago de horas extra (£/hora)',
    'Weekend pay (£/hour)': 'Pago de fin de semana (£/hora)',
    'Base location': 'Ubicación base',
    'Travel range (km)': 'Radio de desplazamiento (km)',
    'Unavailable dates': 'Fechas no disponibles',
    'Dates this worker cannot be deployed. The worker can mark their own from their sign-in; anything here is on record.': 'Fechas en las que este trabajador no puede ser desplegado. El trabajador puede marcar las suyas desde su inicio de sesión; todo lo que aparece aquí queda registrado.',
    'Add date': 'Añadir fecha',
    'No unavailable dates recorded.': 'No hay fechas no disponibles registradas.',
    'No unavailable dates marked.': 'No hay fechas no disponibles marcadas.',
    'Rates and location saved.': 'Tarifas y ubicación guardadas.',

    /* assignment rates */
    'Hourly rates. The worker\x27s defaults are filled in; margin is calculated from these and frozen onto the timesheet when it is approved.': 'Tarifas por hora. Se rellenan con los valores predeterminados del trabajador; el margen se calcula a partir de estas y se congela en el parte de horas al aprobarlo.',
    'Pay (£/hour)': 'Pago (£/hora)',
    'Overtime pay': 'Pago de horas extra',
    'Weekend pay': 'Pago de fin de semana',
    'Charge (£/hour)': 'Tarifa al cliente (£/hora)',
    'Overtime charge': 'Tarifa al cliente por horas extra',
    'Weekend charge': 'Tarifa al cliente de fin de semana',

    /* timesheets */
    'One row per assignment per week. Generate from recorded attendance or type the hours; approving freezes the pay and charge totals at the assignment\x27s rates.': 'Una fila por asignación y semana. Genere el parte a partir de la asistencia registrada o escriba las horas; al aprobarlo se congelan los totales de pago y de cobro según las tarifas de la asignación.',
    'Week starting (Monday)': 'Semana que empieza (lunes)',
    'Basic hours': 'Horas básicas',
    'Overtime hours': 'Horas extra',
    'Weekend hours': 'Horas de fin de semana',
    'From attendance': 'Desde la asistencia',
    'Save draft': 'Guardar borrador',
    'Week': 'Semana',
    'Hours (B/OT/W)': 'Horas (B/E/F)',
    'Charge': 'Cobro',
    'Submitted': 'Enviado',
    'Reject': 'Rechazar',
    'Submit': 'Enviar',
    'Enter some hours.': 'Introduzca algunas horas.',
    'Draft timesheet saved.': 'Parte de horas en borrador guardado.',
    'Choose an assignment and a week first.': 'Elija primero una asignación y una semana.',

    /* commercial: margin and invoices */
    'Commercial': 'Comercial',
    'Margin by assignment': 'Margen por asignación',
    'Low margin': 'Margen bajo',
    'Creates a draft invoice from the contractor\x27s approved timesheets in the period. Payment itself happens outside the platform; record the outcome here.': 'Crea una factura borrador a partir de los partes de horas aprobados del contratista en el período. El pago en sí se realiza fuera de la plataforma; registre aquí el resultado.',
    'Period from': 'Período desde',
    'Period to': 'Período hasta',
    'Payment terms (days)': 'Plazo de pago (días)',
    'Create draft invoice': 'Crear factura borrador',
    'Invoice': 'Factura',
    'Period': 'Período',
    'Total': 'Total',
    'Due': 'Vence',
    'Financial alerts': 'Alertas financieras',
    'No approved timesheets for that contractor in the period.': 'No hay partes de horas aprobados de ese contratista en el período.',
    'Choose the contractor and the period.': 'Elija el contratista y el período.',
    'Mark sent': 'Marcar enviada',
    'Mark paid': 'Marcar pagada',
    'Void': 'Anular',
    'Sent': 'Enviada',
    'Paid': 'Pagada',
    'Overdue': 'Vencida',
    'No invoices yet.': 'Aún no hay facturas.',

    /* contractor pipeline */
    'Contractor pipeline': 'Canal de contratistas',
    'Stage, credit limit and payment terms per contractor. New contractors start as an enquiry.': 'Etapa, límite de crédito y plazo de pago por contratista. Los contratistas nuevos empiezan como consulta.',
    'Stage': 'Etapa',
    'Credit limit (£)': 'Límite de crédito (£)',
    'Terms (days)': 'Plazo (días)',
    'Communication log': 'Registro de comunicaciones',
    'Channel': 'Canal',
    'Meeting': 'Reunión',
    'WhatsApp': 'WhatsApp',
    'Enquiry': 'Consulta',
    'Paused': 'En pausa',
    'Choose the contractor and write the note.': 'Elija el contratista y escriba la nota.',

    /* bulk onboarding */
    'Bulk invitations': 'Invitaciones en lote',
    'One email per line. Every line becomes its own invitation; send them from the list above.': 'Un correo por línea. Cada línea se convierte en su propia invitación; envíelas desde la lista de arriba.',
    'Emails — one per line': 'Correos — uno por línea',
    'Create invitations': 'Crear invitaciones',
    'Bulk worker onboarding': 'Alta de trabajadores en lote',
    'One worker per line: full name, email, trade. Each line creates a draft worker record and a linked worker invitation.': 'Un trabajador por línea: nombre completo, correo, oficio. Cada línea crea un registro de trabajador en borrador y una invitación vinculada.',
    'Workers — name, email, trade': 'Trabajadores — nombre, correo, oficio',
    'Create workers and invite': 'Crear trabajadores e invitar',
    'Enter at least one valid email address, one per line.': 'Introduzca al menos un correo válido, uno por línea.',
    'Choose the contractor these people belong to.': 'Elija a qué contratista pertenece esta gente.',
    'Enter one worker per line: name, email, trade.': 'Introduzca un trabajador por línea: nombre, correo, oficio.',

    /* worker availability self-service */
    'My availability': 'Mi disponibilidad',
    'Mark the dates you cannot work so the team does not put you forward for them.': 'Marque las fechas en las que no puede trabajar para que el equipo no le proponga para ellas.',
    'Choose a date.': 'Elija una fecha.',
    'That date is already marked.': 'Esa fecha ya está marcada.',

    /* shared */
    'Save': 'Guardar',
    'Delete': 'Eliminar',
    'Approve': 'Aprobar',
    '@e.g. Guildford': '@p. ej., Guildford',
    '@e.g. Ana Silva, ana@example.com, painter and decorator': '@p. ej., Ana Silva, ana@example.com, pintora y decoradora'
  };

  var PT = {
    /* sign-in and access */
    'Sign in': 'Iniciar sessão',
    'For the PRJGENUI team, contractors and registered workers.': 'Para a equipa PRJGENUI, empreiteiros e trabalhadores registados.',
    'Email': 'Correio eletrónico',
    'Password': 'Palavra-passe',
    'Forgot your password?': 'Esqueceu a palavra-passe?',
    'Have an invitation code?': 'Tem um código de convite?',
    'Set up your access': 'Configure o seu acesso',
    'Enter your invitation details and choose a password.': 'Introduza os dados do seu convite e escolha uma palavra-passe.',
    'Choose a password': 'Escolha uma palavra-passe',
    'Invitation code': 'Código de convite',
    'Create my account': 'Criar a minha conta',
    'You will receive an email to confirm your address. After confirming, sign in here and your access finishes setting up on its own.': 'Receberá um correio eletrónico para confirmar o seu endereço. Após confirmar, inicie sessão aqui e o seu acesso termina de se configurar sozinho.',
    'Back to sign in': 'Voltar ao início de sessão',
    'Access is by invitation only. If you cannot sign in, write to hello@prjgenuiworkforce.co.uk.': 'O acesso é apenas por convite. Se não conseguir iniciar sessão, escreva para hello@prjgenuiworkforce.co.uk.',
    '— we will email you a link to set a new one.': '— enviaremos por correio eletrónico uma ligação para definir uma nova.',
    'Welcome': 'Bem-vindo',
    'Sign out': 'Terminar sessão',
    'Loading your profile…': 'A carregar o seu perfil…',
    'Loading…': 'A carregar…',
    'Your account is not linked yet': 'A sua conta ainda não está ligada',
    'Your sign-in works, but no role has been assigned to it. If you have an invitation code, enter it below to finish setting up.': 'O seu início de sessão funciona, mas ainda não lhe foi atribuído um papel. Se tiver um código de convite, introduza-o abaixo para terminar a configuração.',
    'Finish setup': 'Terminar configuração',

    /* two-factor */
    'Set up two-factor': 'Configurar a verificação em dois passos',
    'Two-factor verification': 'Verificação em dois passos',
    'Enter the 6-digit code from your authenticator app.': 'Introduza o código de 6 dígitos da sua aplicação de autenticação.',
    'Admin accounts need an authenticator app (Google Authenticator, Microsoft Authenticator or similar). Scan the code with the app, then enter the 6-digit code it shows.': 'As contas de administração precisam de uma aplicação de autenticação (Google Authenticator, Microsoft Authenticator ou semelhante). Leia o código com a aplicação e introduza o código de 6 dígitos que esta mostrar.',
    'Or enter this code manually in your app:': 'Ou introduza este código manualmente na sua aplicação:',
    '6-digit code': 'Código de 6 dígitos',
    'Verify': 'Verificar',
    'Use a different account': 'Usar outra conta',

    /* header and dashboard */
    'Team platform': 'Plataforma da equipa',
    'Compliance Action Centre': 'Centro de ações de conformidade',
    'Run reminders': 'Executar lembretes',
    'Recompute schedule': 'Recalcular o calendário',
    'Workers': 'Trabalhadores',
    'Crews': 'Equipas',
    'Workforce requests': 'Pedidos de pessoal',
    'Assignments': 'Atribuições',
    'Attendance': 'Assistência',
    'Replacement incidents': 'Incidentes de substituição',
    'Invitations': 'Convites',
    'Prices': 'Preços',

    /* roles */
    'Owner': 'Proprietário',
    'Operations': 'Operações',
    'Compliance': 'Conformidade',
    'Contractor': 'Empreiteiro',
    'Worker': 'Trabalhador',
    'Supplier': 'Fornecedor',
    'Auditor': 'Auditor',

    /* worker records */
    'Full name': 'Nome completo',
    'Trade': 'Ofício',
    'Add worker': 'Adicionar trabalhador',
    'Passport': 'Passaporte',
    'Name': 'Nome',
    'Status': 'Estado',
    'Open': 'Abrir',
    'Close': 'Fechar',
    'Advance status': 'Avançar estado',
    'Reason (required to block or archive)': 'Motivo (obrigatório para bloquear ou arquivar)',
    'Reason (recorded permanently)': 'Motivo (registado permanentemente)',
    'Block': 'Bloquear',
    'Archive': 'Arquivar',
    'Invite to sign in': 'Convidar a iniciar sessão',
    'Run readiness check': 'Executar verificação de preparação',
    'Readiness': 'Preparação',
    'Overrides': 'Exceções',
    'An override relaxes one requirement for this worker for a time. It never edits a check, and it is recorded permanently.': 'Uma exceção dispensa um requisito deste trabalhador durante algum tempo. Nunca altera uma verificação e fica registada permanentemente.',
    'Requirement': 'Requisito',
    'Approve override': 'Aprovar exceção',
    'Expires': 'Caduca',
    'Documents': 'Documentos',
    'Identity documents are restricted. Only the Owner and Compliance can open them.': 'Os documentos de identidade são restritos. Apenas o Proprietário e a Conformidade os podem abrir.',
    'Right to Work checks': 'Verificações de direito a trabalhar',
    'Right to Work': 'Direito a trabalhar',
    'Method': 'Método',
    'Home Office share code': 'Código de partilha do Home Office',
    'Manual passport check': 'Verificação manual do passaporte',
    'Check date': 'Data da verificação',
    'Result': 'Resultado',
    'Pass': 'Aprovado',
    'Fail': 'Não aprovado',
    'Follow-up required': 'Requer seguimento',
    'Follow-up due': 'Seguimento devido a',
    'Source': 'Origem',
    'Record check': 'Registar verificação',
    'Cards and training': 'Cartões e formação',
    'Category': 'Categoria',
    'Card or qualification': 'Cartão ou qualificação',
    'Training': 'Formação',
    'Type': 'Tipo',
    'Number (cards)': 'Número (cartões)',
    'Expiry': 'Caducidade',
    'Valid until': 'Válido até',
    'Expires on that date': 'Caduca nessa data',
    'Renewable — renews before it': 'Renovável — renova antes',
    'Permanent — no expiry': 'Permanente — sem caducidade',
    'Add': 'Adicionar',
    'My passport': 'O meu passaporte',
    'Cards, qualifications and training': 'Cartões, qualificações e formação',
    'Skill evidence and work history': 'Evidências de competências e histórico de trabalho',
    'My attendance': 'A minha assistência',
    'If a record is wrong, dispute it — the team must review it before it changes, and the original stays on record either way.': 'Se um registo estiver errado, conteste-o — a equipa deve revê-lo antes de ser alterado, e o original fica registado em qualquer caso.',
    'Assignment': 'Atribuição',
    'Date': 'Data',
    'Outcome': 'Resultado',
    'Performance': 'Desempenho',
    'Reminders': 'Lembretes',
    'My details': 'Os meus dados',
    'Corrections go to the team straight away. Your name, passport number and status can only be changed by the team.': 'As correções chegam à equipa de imediato. O seu nome, número de passaporte e estado só podem ser alterados pela equipa.',
    'Phone': 'Telefone',
    'Availability': 'Disponibilidade',
    'Save corrections': 'Guardar correções',
    'My documents': 'Os meus documentos',
    'Replacement evidence': 'Evidência de substituição',
    'Passport or ID': 'Passaporte ou documento de identidade',
    'Certificate': 'Certificado',
    'Other': 'Outro',
    'File': 'Ficheiro',
    'Upload': 'Carregar',
    'CSCS card': 'Cartão CSCS',
    'Worker record': 'Registo do trabalhador',
    'Worker record not verified': 'Registo do trabalhador não verificado',
    'Right to Work check missing': 'Falta a verificação de direito a trabalhar',
    'Right to Work check did not pass': 'A verificação de direito a trabalhar não foi aprovada',
    'Right to Work follow-up overdue': 'Seguimento do direito a trabalhar em atraso',

    /* worker statuses */
    'Draft': 'Rascunho',
    'In review': 'Em revisão',
    'Verified': 'Verificado',
    'Expiring soon': 'Caduca em breve',
    'Blocked': 'Bloqueado',
    'Archived': 'Arquivado',
    'Pending review': 'Pendente de revisão',
    'Rejected': 'Rejeitado',

    /* crews */
    'A crew is a group of workers with a track record of working well together. A crew only exists once you have seen it happen.': 'Uma equipa é um grupo de trabalhadores com histórico de trabalharem bem juntos. Uma equipa só existe quando já o viu acontecer.',
    'Add crew': 'Adicionar equipa',
    'Crew': 'Equipa',
    'Members': 'Membros',
    'Specialism': 'Especialidade',
    'Evidence': 'Evidência',
    'Crew name': 'Nome da equipa',
    'Supervisor': 'Supervisor',
    'None set': 'Não definido',
    'Ctrl/Cmd-click to select more than one.': 'Ctrl/Cmd-clique para selecionar mais do que um.',
    'Notes': 'Notas',
    'Deployment history': 'Histórico de implantações',
    'Log each time this crew went out together.': 'Registe cada vez que esta equipa saiu a trabalhar.',
    'Client': 'Cliente',
    'Project': 'Projeto',
    '+ Add deployment': '+ Adicionar implantação',
    'Delete crew': 'Eliminar equipa',
    'Cancel': 'Cancelar',
    'Save crew': 'Guardar equipa',

    /* requests and matching */
    'Add a contractor': 'Adicionar um empreiteiro',
    'Company name': 'Nome da empresa',
    'Contact name': 'Pessoa de contacto',
    'Add contractor': 'Adicionar empreiteiro',
    'Choose…': 'Escolher…',
    'Workers needed': 'Trabalhadores necessários',
    'Start date': 'Data de início',
    'Start': 'Início',
    'End': 'Fim',
    'Duration': 'Duração',
    'Create request': 'Criar pedido',
    'Asbestos awareness': 'Sensibilização para o amianto',
    'Working at height': 'Trabalho em altura',
    'Manual handling': 'Manuseamento manual de cargas',
    'Urgent': 'Urgente',
    'Ref': 'Ref',
    'Needed': 'Necessários',
    'Matches': 'Correspondências',
    'View matches': 'Ver correspondências',
    'Run matching': 'Executar correspondência',
    'Put forward': 'Proposto',
    'Held back': 'Descartado',
    'Approve match': 'Aprovar correspondência',
    'Send offer': 'Enviar oferta',
    'Factor': 'Fator',
    'Reason': 'Motivo',
    'Worker record is verified': 'O registo do trabalhador está verificado',
    'Right to Work check is current': 'A verificação de direito a trabalhar está válida',
    'Trade matches the request': 'O ofício corresponde ao pedido',
    'Request': 'Pedido',
    'Open': 'Aberto',

    /* request statuses */
    'Matched': 'Com correspondências',
    'Offered': 'Oferta enviada',
    'Filled': 'Preenchido',
    'Closed': 'Fechado',

    /* assignments lifecycle */
    'Proposed': 'Proposta',
    'Accepted': 'Aceite',
    'Confirmed': 'Confirmada',
    'Activate': 'Ativar',
    'Active': 'Ativa',
    'Completed': 'Concluída',
    'Cancelled': 'Cancelada',
    'No show': 'Não compareceu',
    'Replaced': 'Substituída',
    'History': 'Histórico',
    'Legacy': 'Histórica',
    'Declined': 'Recusada',
    'Confirm': 'Confirmar',
    'Record outcome': 'Registar resultado',
    'Worker attended': 'O trabalhador compareceu',
    'Yes': 'Sim',
    'No': 'Não',
    'Rating': 'Avaliação',
    '1 — poor': '1 — fraco',
    '5 — excellent': '5 — excelente',
    'Would rehire': 'Contrataria novamente',
    'Undecided': 'Por decidir',
    'Client feedback': 'Comentários do cliente',
    'Save outcome': 'Guardar resultado',
    'Back': 'Voltar',
    'Assignment rates': 'Tarifas da atribuição',
    'Records only. Billing is built on top of these in a later stage.': 'Apenas registos. A faturação será construída sobre estes valores numa fase posterior.',
    'Worker pay rate': 'Tarifa do trabalhador',
    'Client charge rate': 'Tarifa cobrada ao cliente',
    'Save rates': 'Guardar tarifas',
    'Statement': 'Extrato',
    'Rates': 'Tarifas',

    /* attendance */
    'One record per assignment and shift date. The existing record is the authoritative one — dispute it to correct it.': 'Um registo por atribuição e data de turno. O registo existente é o que vale — conteste-o para o corrigir.',
    'Shift date': 'Data do turno',
    'Attended': 'Compareceu',
    'Late': 'Com atraso',
    'Excused': 'Justificado',
    'Not recorded': 'Não registado',
    'Record attendance': 'Registar assistência',
    'Dispute': 'Contestar',
    'Resolve dispute': 'Resolver contestação',
    'Resolution': 'Resolução',
    'Original stands': 'O original mantém-se',
    'Corrected': 'Corrigido',
    'Withdrawn by the worker': 'Retirado pelo trabalhador',
    'Corrected outcome (corrections only)': 'Resultado corrigido (apenas correções)',
    'Resolve': 'Resolver',
    'Recorded': 'Registado',
    'Disputed': 'Contestado',

    /* replacement incidents */
    'Cancellation': 'Cancelamento',
    'Replacement required': 'Substituição necessária',
    'Record incident': 'Registar incidente',
    'Replacement': 'Substituição',
    'Incident': 'Incidente',
    'Record approval': 'Registar aprovação',
    'Approved': 'Aprovado',
    'Refused': 'Recusado',
    'Approval note': 'Nota de aprovação',
    'Add approval': 'Adicionar aprovação',
    'Link replacement (same request, created through the offer flow)': 'Ligar substituição (mesmo pedido, criado através do fluxo de oferta)',
    'Link': 'Ligar',
    'Acknowledge site pack': 'Confirmar receção do dossier de obra',
    'Resolve chain': 'Resolver cadeia',

    /* invitations */
    'Create an invitation by email and role. Each one expires after seven days if unused.': 'Crie um convite por correio eletrónico e papel. Cada um caduca ao fim de sete dias se não for usado.',
    'Role': 'Papel',
    'Invite': 'Convidar',
    'Copy link': 'Copiar ligação',
    'Email invitee': 'Enviar correio ao convidado',
    'Revoke': 'Revogar',
    'pending': 'pendente',
    'Invitation emails are sent automatically once the invitation flow is connected in the next build step.': 'Os correios de convite são enviados automaticamente quando o fluxo de convites for ligado na próxima fase.',

    /* prices, switches, costs */
    'Scope': 'Âmbito',
    'Standard': 'Standard',
    'Customer-specific': 'Específico do cliente',
    'Contractor (customer prices)': 'Empreiteiro (preços de cliente)',
    'Service': 'Serviço',
    'Managed onboarding': 'Incorporação gerida',
    'Compliance monitoring': 'Monitorização de conformidade',
    'Training-request coordination': 'Coordenação de pedidos de formação',
    'Right to Work check': 'Verificação de direito a trabalhar',
    'Price (£)': 'Preço (£)',
    'Price': 'Preço',
    'Unit': 'Unidade',
    'VAT rate (%)': 'Taxa de IVA (%)',
    'Billing frequency': 'Frequência de faturação',
    'Minimum monthly (£)': 'Mínimo mensal (£)',
    'Discount (%)': 'Desconto (%)',
    'Discount reason (required with a discount)': 'Motivo do desconto (obrigatório com um desconto)',
    'Add price': 'Adicionar preço',
    'Approval': 'Aprovação',
    'Service switches': 'Serviços ativos',
    'Save switches': 'Guardar serviços',
    'Onboarding': 'Incorporação',
    'Monitoring': 'Monitorização',
    'Training': 'Formação',
    'From': 'Desde',
    'External costs': 'Custos externos',
    'Description': 'Descrição',
    'Training provider': 'Fornecedor de formação',
    'Identity check': 'Verificação de identidade',
    'Verification': 'Verificação',
    'Amount (£)': 'Montante (£)',
    'Amount': 'Montante',
    'Record cost': 'Registar custo',
    'Your company': 'A sua empresa',
    'Assignment statements': 'Extratos de atribuição',
    'Generate new version': 'Gerar nova versão',
    'Assignment statement': 'Extrato da atribuição',

    /* footer */
    'PRJGENUI Workforce — internal platform. Not for public distribution.': 'PRJGENUI Workforce — plataforma interna. Não para distribuição pública.',

    /* a few common runtime messages */
    'That email and password did not match an account. Check both and try again.': 'Esse correio eletrónico e palavra-passe não correspondem a nenhuma conta. Verifique ambos e tente novamente.',
    'Enter the check date.': 'Introduza a data da verificação.',
    'Configuration is missing, so sign-in is not available here.': 'Falta a configuração, pelo que o início de sessão não está disponível aqui.',
    'Record feedback': 'Registar comentários',
    'PRJGENUI Workforce — Team sign-in': 'PRJGENUI Workforce — Iniciar sessão',

    /* placeholders */
    '@e.g. painter and decorator': 'p. ex., pintor e decorador',
    '@e.g. Home Office online service': 'p. ex., serviço online do Home Office',
    '@e.g. cscs, ipaf, asbestos awareness': 'p. ex., cscs, ipaf, amianto',
    '@e.g. Painting crew A': 'p. ex., Equipa de pintura A',
    '@e.g. Education / occupied housing': 'p. ex., Educação / habitação ocupada',
    '@e.g. Southwark Builds Ltd': 'p. ex., Construções Sul Lda.',
    '@e.g. 2 weeks': 'p. ex., 2 semanas',
    '@How the job went, from the client\x27s side': 'Como correu o trabalho, do lado do cliente',
    '@e.g. £180/day': 'p. ex., 180 £/dia',
    '@e.g. £220/day': 'p. ex., 220 £/dia',
    '@e.g. site log, supervisor call': 'p. ex., registo de obra, chamada do supervisor',
    '@e.g. per worker per month': 'p. ex., por trabalhador por mês',
    '@e.g. monthly': 'p. ex., mensal',

    /* ---- commercial and growth layer (migration 0026) ---- */

    /* control tower */
    'Control Tower': 'Torre de controlo',
    'Alerts': 'Alertas',
    'No alerts. Fill rate, margins, payments and compliance are all healthy.': 'Sem alertas. A taxa de cobertura, as margens, os pagamentos e a conformidade estão saudáveis.',
    'Reports and exports': 'Relatórios e exportações',
    'Each button downloads a CSV of the current data — workers, assignments, approved timesheets (payroll-ready), invoices and attendance.': 'Cada botão descarrega um CSV com os dados atuais: trabalhadores, atribuições, folhas de horas aprovadas (prontas para os salários), faturas e assiduidade.',
    'Timesheets (payroll)': 'Folhas de horas (salários)',
    'Invoices': 'Faturas',
    'Workers on file': 'Trabalhadores registados',
    'Verified workers': 'Trabalhadores verificados',
    'Available now': 'Disponíveis agora',
    'Active contractors': 'Empreiteiros ativos',
    'Open requests': 'Pedidos abertos',
    'Active assignments': 'Atribuições ativas',
    'Fill rate (30d)': 'Taxa de cobertura (30 d)',
    'Time to fill (30d)': 'Tempo para cobrir (30 d)',
    'Attendance (30d)': 'Assiduidade (30 d)',
    'No-shows (30d)': 'Faltas (30 d)',
    'Open replacements': 'Substituições abertas',
    'Expiring compliance': 'Conformidade a expirar',
    'Payment exposure': 'Exposição a pagamentos',
    'Overdue invoices': 'Faturas vencidas',
    'Approved revenue': 'Receitas aprovadas',
    'No overdue invoices.': 'Não há faturas vencidas.',

    /* workers: search, rates and availability */
    'Search workers': 'Procurar trabalhadores',
    'Name, trade or passport number': 'Nome, ofício ou número de passaporte',
    'Rates and availability': 'Tarifas e disponibilidade',
    'Default hourly rates are copied into new assignments. Travel range and base location feed capacity planning.': 'As tarifas horárias predefinidas são copiadas para as novas atribuições. O raio de deslocação e a localização de base alimentam o planeamento de capacidade.',
    'Default pay (£/hour)': 'Pagamento predefinido (£/hora)',
    'Overtime pay (£/hour)': 'Pagamento de horas extra (£/hora)',
    'Weekend pay (£/hour)': 'Pagamento de fim de semana (£/hora)',
    'Base location': 'Localização de base',
    'Travel range (km)': 'Raio de deslocação (km)',
    'Unavailable dates': 'Datas indisponíveis',
    'Dates this worker cannot be deployed. The worker can mark their own from their sign-in; anything here is on record.': 'Datas em que este trabalhador não pode ser destacado. O trabalhador pode marcar as suas a partir do seu início de sessão; tudo o que aqui aparece fica registado.',
    'Add date': 'Adicionar data',
    'No unavailable dates recorded.': 'Não há datas de indisponibilidade registadas.',
    'No unavailable dates marked.': 'Não há datas de indisponibilidade marcadas.',
    'Rates and location saved.': 'Tarifas e localização guardadas.',

    /* assignment rates */
    'Hourly rates. The worker\x27s defaults are filled in; margin is calculated from these and frozen onto the timesheet when it is approved.': 'Tarifas por hora. São preenchidas com os valores predefinidos do trabalhador; a margem é calculada a partir delas e fixada na folha de horas quando esta é aprovada.',
    'Pay (£/hour)': 'Pagamento (£/hora)',
    'Overtime pay': 'Pagamento de horas extra',
    'Weekend pay': 'Pagamento de fim de semana',
    'Charge (£/hour)': 'Tarifa ao cliente (£/hora)',
    'Overtime charge': 'Tarifa ao cliente de horas extra',
    'Weekend charge': 'Tarifa ao cliente de fim de semana',

    /* timesheets */
    'One row per assignment per week. Generate from recorded attendance or type the hours; approving freezes the pay and charge totals at the assignment\x27s rates.': 'Uma linha por atribuição e semana. Gere a folha a partir da assiduidade registada ou escreva as horas; a aprovação fixa os totais de pagamento e de cobrança às tarifas da atribuição.',
    'Week starting (Monday)': 'Semana a começar (segunda-feira)',
    'Basic hours': 'Horas normais',
    'Overtime hours': 'Horas extra',
    'Weekend hours': 'Horas de fim de semana',
    'From attendance': 'A partir da assiduidade',
    'Save draft': 'Guardar rascunho',
    'Week': 'Semana',
    'Hours (B/OT/W)': 'Horas (N/E/F)',
    'Charge': 'Cobrança',
    'Submitted': 'Submetida',
    'Reject': 'Rejeitar',
    'Submit': 'Submeter',
    'Enter some hours.': 'Introduza algumas horas.',
    'Draft timesheet saved.': 'Folha de horas em rascunho guardada.',
    'Choose an assignment and a week first.': 'Escolha primeiro uma atribuição e uma semana.',

    /* commercial: margin and invoices */
    'Commercial': 'Comercial',
    'Margin by assignment': 'Margem por atribuição',
    'Low margin': 'Margem baixa',
    'Creates a draft invoice from the contractor\x27s approved timesheets in the period. Payment itself happens outside the platform; record the outcome here.': 'Cria uma fatura rascunho a partir das folhas de horas aprovadas do empreiteiro no período. O pagamento em si acontece fora da plataforma; registe aqui o desfecho.',
    'Period from': 'Período desde',
    'Period to': 'Período até',
    'Payment terms (days)': 'Prazo de pagamento (dias)',
    'Create draft invoice': 'Criar fatura rascunho',
    'Invoice': 'Fatura',
    'Period': 'Período',
    'Total': 'Total',
    'Due': 'Vence',
    'Financial alerts': 'Alertas financeiras',
    'No approved timesheets for that contractor in the period.': 'Não há folhas de horas aprovadas desse empreiteiro no período.',
    'Choose the contractor and the period.': 'Escolha o empreiteiro e o período.',
    'Mark sent': 'Marcar enviada',
    'Mark paid': 'Marcar paga',
    'Void': 'Anular',
    'Sent': 'Enviada',
    'Paid': 'Paga',
    'Overdue': 'Vencida',
    'No invoices yet.': 'Ainda não há faturas.',

    /* contractor pipeline */
    'Contractor pipeline': 'Gestão de empreiteiros',
    'Stage, credit limit and payment terms per contractor. New contractors start as an enquiry.': 'Etapa, limite de crédito e prazo de pagamento por empreiteiro. Os empreiteiros novos começam como consulta.',
    'Stage': 'Etapa',
    'Credit limit (£)': 'Limite de crédito (£)',
    'Terms (days)': 'Prazo (dias)',
    'Communication log': 'Registo de comunicações',
    'Channel': 'Canal',
    'Meeting': 'Reunião',
    'WhatsApp': 'WhatsApp',
    'Enquiry': 'Consulta',
    'Paused': 'Em pausa',
    'Choose the contractor and write the note.': 'Escolha o empreiteiro e escreva a nota.',

    /* bulk onboarding */
    'Bulk invitations': 'Convites em massa',
    'One email per line. Every line becomes its own invitation; send them from the list above.': 'Um correio por linha. Cada linha torna-se num convite próprio; envie-os a partir da lista acima.',
    'Emails — one per line': 'Correios — um por linha',
    'Create invitations': 'Criar convites',
    'Bulk worker onboarding': 'Ingresso de trabalhadores em massa',
    'One worker per line: full name, email, trade. Each line creates a draft worker record and a linked worker invitation.': 'Um trabalhador por linha: nome completo, correio, ofício. Cada linha cria um registo de trabalhador em rascunho e um convite associado.',
    'Workers — name, email, trade': 'Trabalhadores — nome, correio, ofício',
    'Create workers and invite': 'Criar trabalhadores e convidar',
    'Enter at least one valid email address, one per line.': 'Introduza pelo menos um endereço de correio válido, um por linha.',
    'Choose the contractor these people belong to.': 'Escolha a que empreiteiro estas pessoas pertencem.',
    'Enter one worker per line: name, email, trade.': 'Introduza um trabalhador por linha: nome, correio, ofício.',

    /* worker availability self-service */
    'My availability': 'A minha disponibilidade',
    'Mark the dates you cannot work so the team does not put you forward for them.': 'Marque as datas em que não pode trabalhar para que a equipa não o proponha para elas.',
    'Choose a date.': 'Escolha uma data.',
    'That date is already marked.': 'Essa data já está marcada.',

    /* shared */
    'Note': 'Nota',
    'Save': 'Guardar',
    'Delete': 'Eliminar',
    'Approve': 'Aprovar',
    '@e.g. Guildford': '@p. ex., Guildford',
    '@e.g. Ana Silva, ana@example.com, painter and decorator': '@p. ex., Ana Silva, ana@example.com, pintora e decoradora'
  };

  var DICTS = { es: ES, pt: PT };

  var MONTHS = {
    es: { Jan: 'Ene', Feb: 'Feb', Mar: 'Mar', Apr: 'Abr', May: 'May', Jun: 'Jun',
          Jul: 'Jul', Aug: 'Ago', Sep: 'Sep', Oct: 'Oct', Nov: 'Nov', Dec: 'Dic' },
    pt: { Jan: 'Jan', Feb: 'Fev', Mar: 'Mar', Apr: 'Abr', May: 'Mai', Jun: 'Jun',
          Jul: 'Jul', Aug: 'Ago', Sep: 'Set', Oct: 'Out', Nov: 'Nov', Dec: 'Dez' }
  };

  /* pattern rules for strings the dictionaries cannot key exactly */
  var RULES = [
    { re: /^Hello,\s(.*)$/, es: 'Hola, $1', pt: 'Olá, $1' },
    { re: /^Matches — (.+)$/, es: 'Coincidencias — $1', pt: 'Correspondências — $1' },
    { re: /^Put forward #(\d+)$/, es: 'Propuesto #$1', pt: 'Proposto #$1' },
    { re: /^Ready — (.+)$/, es: 'Listo — $1', pt: 'Pronto — $1' },
    { re: /^Expires in (\d+) days?$/, es: 'Caduca en $1 días', pt: 'Caduca em $1 dias' },
    /* commercial and growth layer */
    { re: /^Assignment rates — (.+)$/, es: 'Tarifas de la asignación — $1', pt: 'Tarifas da atribuição — $1' },
    { re: /^(\d+) attendance records found — check the hours and save the draft\.$/, es: 'Se encontraron $1 registros de asistencia — revise las horas y guarde el borrador.', pt: 'Foram encontrados $1 registos de assiduidade — verifique as horas e guarde o rascunho.' },
    { re: /^Average margin ([\d.]+)% across (\d+) rated assignments, (\d+) below (\d+)%\.$/, es: 'Margen medio del $1% en $2 asignaciones con tarifas, $3 por debajo del $4%.', pt: 'Margem média de $1% em $2 atribuições com tarifas, $3 abaixo de $4%.' },
    { re: /^(INV-\d{6}) created with (\d+) lines?\.$/, es: '$1 creada con $2 líneas.', pt: '$1 criada com $2 linhas.' },
    { re: /^Overdue invoices: (\d+)\.$/, es: 'Facturas vencidas: $1.', pt: 'Faturas vencidas: $1.' },
    { re: /^No-shows \(last 30 days\): (\d+)\.$/, es: 'Ausencias (últimos 30 días): $1.', pt: 'Faltas (últimos 30 dias): $1.' },
    { re: /^Unresolved replacement incidents: (\d+)\.$/, es: 'Incidentes de sustitución sin resolver: $1.', pt: 'Incidentes de substituição por resolver: $1.' },
    { re: /^Compliance items expired or due within 30 days: (\d+)\.$/, es: 'Elementos de cumplimiento caducados o por caducar en 30 días: $1.', pt: 'Itens de conformidade expirados ou a expirar em 30 dias: $1.' },
    { re: /^Payment exposure \(sent, unpaid\): (.+)\.$/, es: 'Exposición de pagos (enviadas, sin pagar): $1.', pt: 'Exposição a pagamentos (enviadas, não pagas): $1.' },
    { re: /^Worker pay liability \(approved, not yet invoiced\): (.+)\.$/, es: 'Obligación de pago a trabajadores (aprobado, aún sin facturar): $1.', pt: 'Responsabilidade de pagamento a trabalhadores (aprovada, ainda não faturada): $1.' },
    { re: /^Approved timesheet revenue to date: (.+)\.$/, es: 'Ingresos por partes de horas aprobados hasta la fecha: $1.', pt: 'Receitas de folhas de horas aprovadas até à data: $1.' },
    { re: /^As at (.+)$/, es: 'A fecha de $1', pt: 'À data de $1' },
    { re: /^Demand by trade \(open requests\): (.+)$/, es: 'Demanda por oficio (solicitudes abiertas): $1', pt: 'Procura por ofício (pedidos abertos): $1' },
    { re: /^Remove (.+)$/, es: 'Quitar $1', pt: 'Remover $1' },
    { re: /^([\d.]+) days$/, es: '$1 días', pt: '$1 dias' },
    { re: /^(\d+) invitations created — send each from the list above\.$/, es: 'Se crearon $1 invitaciones — envíelas desde la lista de arriba.', pt: 'Foram criados $1 convites — envie-os a partir da lista acima.' },
    { re: /^(\d+) worker records created with linked invitations \((\d+) failed\) — links are in the Invitations list\.$/, es: 'Se crearon $1 registros de trabajadores con invitaciones vinculadas ($2 fallidas) — los enlaces están en la lista de invitaciones.', pt: 'Foram criados $1 registos de trabalhadores com convites associados ($2 falhados) — as ligações estão na lista de convites.' },
    { re: /^(.+) saved\.$/, es: '$1 guardado.', pt: '$1 guardado.' }
  ];

  var LANG_KEY = 'prjgenui_lang';
  var current = null;
  var translating = false;

  function dict() { return DICTS[current] || null; }

  function convert(text) {
    if (!current || current === 'en') return null;
    var d = dict();
    if (d && Object.prototype.hasOwnProperty.call(d, text)) return d[text];
    for (var i = 0; i < RULES.length; i++) {
      var m = text.match(RULES[i].re);
      if (m) {
        var out = RULES[i][current];
        for (var g = 1; g < m.length; g++) out = out.replace('$' + g, m[g]);
        return out;
      }
    }
    return null;
  }

  function convertDates(text) {
    if (!current || current === 'en') return text;
    var months = MONTHS[current];
    if (!months) return text;
    return text.replace(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/g,
      function (m) { return months[m] || m; });
  }

  function applyToText(node) {
    var raw = node.nodeValue;
    if (!raw || !raw.trim()) return;
    var lead = raw.match(/^\s*/)[0];
    var trail = raw.match(/\s*$/)[0];
    /* the source HTML breaks some strings across lines; the dictionaries
       key on the single-spaced form */
    var core = raw.trim().replace(/\s+/g, ' ');
    var out = convert(core);
    if (out !== null) { node.nodeValue = lead + out + trail; return; }
    if (/\d/.test(core)) {
      var dated = convertDates(core);
      if (dated !== core) node.nodeValue = lead + dated + trail;
    }
  }

  function walk(root) {
    if (root.nodeType === 3) { applyToText(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    var tag = root.nodeType === 1 ? root.tagName.toLowerCase() : '';
    if (tag === 'script' || tag === 'style' || tag === 'select') return;
    if (root.nodeType === 1) {
      var ph = root.getAttribute && root.getAttribute('placeholder');
      if (ph) {
        var p = convert(ph);
        if (p !== null) root.setAttribute('placeholder', p);
      }
    }
    var kids = (root.childNodes || []);
    for (var i = 0; i < kids.length; i++) walk(kids[i]);
  }

  function applyAll() {
    translating = true;
    try {
      walk(document.body);
      if (current === 'en') {
        document.documentElement.setAttribute('lang', 'en-GB');
      } else {
        document.documentElement.setAttribute('lang', current === 'es' ? 'es' : 'pt');
        var t = convert(document.title);
        if (t) document.title = t;
      }
    } finally {
      translating = false;
    }
  }

  /* keep translated while the app re-renders its tables and panels */
  var pending = null;
  var observer = new MutationObserver(function (records) {
    if (translating || current === 'en') return;
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      if (r.type === 'childList' && r.addedNodes.length) { schedule(); break; }
      if (r.type === 'characterData') { schedule(); break; }
    }
  });
  function schedule() {
    if (pending) return;
    pending = setTimeout(function () {
      pending = null;
      applyAll();
    }, 120);
  }
  if (document.body) observer.observe(document.body, { childList: true, subtree: true, characterData: true });

  /* ---- the language selector ---- */
  var LABELS = { en: 'English', es: 'Español', pt: 'Português' };
  var CSS =
    '.prj-lang{position:fixed;top:10px;right:14px;z-index:60;display:flex;align-items:center;gap:6px;' +
    'font:12px/1.4 system-ui,sans-serif;color:#5b5b5b}' +
    '.prj-lang label{opacity:.75}' +
    '.prj-lang select{font:12px/1.4 system-ui,sans-serif;padding:3px 6px;border:1px solid #c9c9c9;' +
    'border-radius:6px;background:#fff;color:#333;cursor:pointer}';

  function buildSelector() {
    if (document.querySelector('.prj-lang')) return;
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    var wrap = document.createElement('div');
    wrap.className = 'prj-lang';
    var label = document.createElement('label');
    label.setAttribute('for', 'prj-lang-select');
    label.textContent = current === 'es' ? 'Idioma' : current === 'pt' ? 'Idioma' : 'Language';
    var sel = document.createElement('select');
    sel.id = 'prj-lang-select';
    ['en', 'es', 'pt'].forEach(function (code) {
      var o = document.createElement('option');
      o.value = code;
      o.textContent = LABELS[code];
      if (code === current) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', function () {
      setLang(sel.value);
    });
    wrap.appendChild(label);
    wrap.appendChild(sel);
    document.body.appendChild(wrap);
  }

  function setLang(lang) {
    current = lang;
    try { localStorage.setItem(LANG_KEY, lang); } catch (e) {}
    /* always reload: the dictionaries translate from English, so every
       switch starts from the pristine page and applies the new language
       on load */
    location.reload();
  }

  /* ---- boot ---- */
  /* the public site's Spanish and Portuguese pages link here as
     app/#lang=es / app/#lang=pt so a visitor arrives in the language they
     were already reading; read it once, remember it, clean the URL */
  var m = /^#lang=(en|es|pt)$/.exec(location.hash || '');
  if (m) {
    try { localStorage.setItem(LANG_KEY, m[1]); } catch (e) {}
    current = m[1];
    history.replaceState(null, '', location.pathname + location.search);
  } else {
    try { current = localStorage.getItem(LANG_KEY) || 'en'; } catch (e) { current = 'en'; }
  }
  if (!DICTS[current] && current !== 'en') current = 'en';

  function boot() {
    buildSelector();
    if (current !== 'en') applyAll();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
