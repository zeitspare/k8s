{{/* ######### SMTP templates */}}

{{/*
  Generates smtp settings for ActionMailer to be used in webservice and sidekiq
*/}}
{{- define "gitlab.smtp_settings" -}}
{{- if .Values.global.smtp.enabled -}}
smtp_settings = {
  address: {{ .Values.global.smtp.address | quote }},
  port: {{ .Values.global.smtp.port | int }},
  ca_file: "/etc/ssl/certs/ca-certificates.crt",
  {{- if .Values.global.smtp.domain }}
  domain: {{ .Values.global.smtp.domain | quote }},
  {{- end }}
  {{ if has .Values.global.smtp.authentication (list "login" "plain" "cram_md5") }}
  authentication: :{{.Values.global.smtp.authentication}},
  user_name: {{ .Values.global.smtp.user_name | quote }},
  password: File.read("/etc/gitlab/smtp/smtp-password").strip,
  {{- end }}
  {{- if .Values.global.smtp.starttls_auto }}
  enable_starttls_auto: true,
  {{- else }}
  enable_starttls_auto: false,
  {{- end }}
  {{- if has .Values.global.smtp.tls (list true false) }}
  tls: {{ .Values.global.smtp.tls }},
  {{- end }}
  {{- if .Values.global.smtp.openssl_verify_mode }}
  openssl_verify_mode: {{ .Values.global.smtp.openssl_verify_mode | quote }},
  {{- end }}
  {{- if .Values.global.smtp.open_timeout }}
  open_timeout: {{ .Values.global.smtp.open_timeout | int }},
  {{- end }}
  {{- if .Values.global.smtp.read_timeout }}
  read_timeout: {{ .Values.global.smtp.read_timeout | int }}
  {{- end }}
}

{{ if eq .Values.global.smtp.pool true -}}
require 'mail/smtp_pool'

ActionMailer::Base.add_delivery_method :smtp_pool, Mail::SMTPPool

Gitlab::Application.config.action_mailer.delivery_method = :smtp_pool
ActionMailer::Base.delivery_method = :smtp_pool

ActionMailer::Base.smtp_pool_settings = {
  pool: Mail::SMTPPool.create_pool(
    smtp_settings.merge(pool_size: Gitlab::Runtime.max_threads)
  )
}
{{- else -}}
Rails.application.config.action_mailer.delivery_method = :smtp
ActionMailer::Base.delivery_method = :smtp

ActionMailer::Base.smtp_settings = smtp_settings
{{- end -}}
{{- end -}}
{{- end -}}

{{/* Default from address for emails based on domain */}}
{{- define "gitlab.email.from" -}}
{{ .Values.global.email.from | default (printf "gitlab@%s" .Values.global.hosts.domain ) | quote -}}
{{- end -}}

{{/* Default replyto address for emails based on domain */}}
{{- define "gitlab.email.reply_to" -}}
{{ .Values.global.email.reply_to | default (printf "noreply@%s" .Values.global.hosts.domain ) | quote -}}
{{- end -}}

{{/* Outgoing email settings */}}
{{- define "gitlab.outgoing_email_settings" }}
email_from: {{ template "gitlab.email.from" . }}
email_display_name: {{ .Values.global.email.display_name | quote }}
email_reply_to: {{ template "gitlab.email.reply_to" . }}
email_subject_suffix: {{ .Values.global.email.subject_suffix | quote }}
{{- if .Values.global.email.smime.enabled }}
email_smime:
  enabled: true
  key_file: /home/git/gitlab/.gitlab_smime_key
  cert_file: /home/git/gitlab/.gitlab_smime_cert
{{- end }}
{{- end }}

{{/* microsoftGraphMailer secrets */}}
{{- define "gitlab.appConfig.microsoftGraphMailer.mountSecrets" -}}
# mount secrets for microsoftGraphMailer
{{- if $.Values.global.appConfig.microsoft_graph_mailer.enabled }}
- secret:
    name: {{ $.Values.global.appConfig.microsoft_graph_mailer.client_secret.secret | required "Missing required secret containing the OAuth2 Client ID for outgoing email. Make sure to set `global.appConfig.microsoft_graph_mailer.client_secret.secret`" }}
    items:
      - key: {{ $.Values.global.appConfig.microsoft_graph_mailer.client_secret.key }}
        path: microsoft_graph_mailer/client_secret
{{- end }}
{{- end -}}{{/* "gitlab.appConfig.microsoftGraphMailer.mountSecrets" "*/}}

{{/* SMTP authentication secret */}}
{{- define "gitlab.smtp.mountSecrets" -}}
# mount secrets for SMTP
{{- with $.Values.global.smtp }}
{{-   $isNoneAuth := eq "none" (.authentication | default "none") }}
{{-   if and .enabled (not $isNoneAuth) }}
- secret:
    name: {{ .password.secret | required "Missing required secret containing the SMTP password. Make sure to set `global.smtp.password.secret`" }}
    items:
      - key: {{ .password.key }}
        path: smtp/smtp-password
{{-   end }}
{{- end }}
{{- end }}
