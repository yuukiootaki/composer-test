variable "gcp_project" {
  type = object({
    project_id = string
    region     = string
    zone       = string
  })
  description = "gcp project"
  default = {
    project_id = "PROJECT_ID"
  }
}
