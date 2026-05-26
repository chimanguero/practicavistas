from datetime import datetime, timezone

from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Formulario para crear y editar publicaciones."""

    class Meta:
        model  = Post
        # auto_now_add/auto_now quedan excluidos automáticamente (editable=False)
        fields = ["title", "body", "category", "tags", "published"]
        widgets = {
            "title":     forms.TextInput(attrs={"class": "form-control", "placeholder": "Título de la publicación"}),
            "body":      forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "category":  forms.Select(attrs={"class": "form-select"}),
            "tags":      forms.SelectMultiple(attrs={"class": "form-select", "size": 5}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title":     "Título",
            "body":      "Contenido",
            "category":  "Categoría",
            "tags":      "Etiquetas",
            "published": "¿Publicar?",
        }
        error_messages = {
            "title": {"required": "El título es obligatorio."},
            "body":  {"required": "El contenido es obligatorio."},
        }

    def clean_title(self):
        """Capa 4: validación personalizada con acceso al ORM."""
        title = self.cleaned_data["title"].strip()
        if len(title) < 10:
            raise forms.ValidationError(
                "Mínimo %(min)s caracteres.", params={"min": 10}
            )
        qs = Post.objects.filter(title__iexact=title)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una publicación con ese título.")
        return title

    def clean(self):
        """Capa 5: validación cruzada — publicar requiere contenido mínimo."""
        cleaned   = super().clean()
        body      = cleaned.get("body", "")
        published = cleaned.get("published", False)

        if published and len(body) < 100:
            self.add_error(
                "body",
                "Para publicar, el contenido debe tener al menos 100 caracteres.",
            )
        return cleaned


class CommentForm(forms.ModelForm):
    """Formulario para agregar comentarios a una publicación."""

    class Meta:
        model  = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribí tu comentario...",
            }),
        }
        labels = {"body": "Comentario"}
        error_messages = {"body": {"required": "El comentario no puede estar vacío."}}

class CursoForm(forms.ModelForm):
    """Formulario para crear un curso."""
    class Meta:
        model = Curso
        fields = ["titulo", "Instructor", "fecha_inicio", "fecha_fin"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título del curso"}),
            "Instructor": forms.Select(attrs={"class": "form-select"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "titulo": "Título",
            "Instructor": "Instructor",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de fin",
            "descripcion": "Descripción"
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if (
            fecha_fin is not None
            and fecha_inicio is not None
            and fecha_fin < fecha_inicio
        ):
            self.add_error("fecha_fin", "La fecha de fin debe ser posterior a la fecha de inicio.")
            
        return cleaned_data
    
    def clean_titulo(self):
        titulo = self.cleaned_data["titulo"].strip()
        if len(titulo) < 5:
            raise forms.ValidationError("El título del curso debe tener al menos 5 caracteres.")
        return titulo
    
    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data["fecha_inicio"]
        if fecha_inicio < datetime.date.today():
            raise forms.ValidationError("La fecha de inicio no puede ser antes que hoy.")
        return fecha_inicio
    
    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data["fecha_fin"]
        if fecha_fin < datetime.date.today():
            raise forms.ValidationError("La fecha de fin no puede ser antes que hoy.")
        return fecha_fin