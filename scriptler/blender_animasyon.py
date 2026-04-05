"""
Blender Python scripti - komut satırından çalıştırılır:
blender --background --python scriptler/blender_animasyon.py -- --sahne ninni --sure 10 --cikti animasyonlar/test.mp4
"""
import sys
import os

def blender_scriptini_olustur(sahne_turu, sure_saniye, cikti_dosyasi):
    """Blender'da çalıştırılacak Python scriptini oluşturur"""
    script = f'''
import bpy
import math

# Sahneyi temizle
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Render ayarları
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = {sure_saniye * 30}
scene.render.filepath = r"{cikti_dosyasi}"
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"

# Kamera ekle
bpy.ops.object.camera_add(location=(0, -10, 2))
camera = bpy.context.active_object
camera.data.lens = 35
scene.camera = camera

def sahne_ninni():
    """Mavi/mor gece gökyüzü, ay ve yıldızlar"""
    # Arkaplan rengi
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.02, 0.02, 0.15, 1)  # Koyu mavi

    # Ay - büyük sarı küre
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(3, 0, 3))
    ay = bpy.context.active_object
    ay.name = "Ay"
    mat_ay = bpy.data.materials.new("AyMalzeme")
    mat_ay.use_nodes = True
    mat_ay.node_tree.nodes["Principled BSDF"].inputs[26].default_value = (1.0, 0.9, 0.3, 1)
    mat_ay.node_tree.nodes["Principled BSDF"].inputs[27].default_value = 3.0
    ay.data.materials.append(mat_ay)

    # Yıldızlar
    import random
    random.seed(42)
    for i in range(30):
        x = random.uniform(-8, 8)
        y = random.uniform(0, 2)
        z = random.uniform(-3, 5)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, y, z))
        yildiz = bpy.context.active_object
        yildiz.name = f"Yildiz_{{i}}"
        mat_y = bpy.data.materials.new(f"YildizMat_{{i}}")
        mat_y.use_nodes = True
        mat_y.node_tree.nodes["Principled BSDF"].inputs[26].default_value = (1, 1, 0.8, 1)
        mat_y.node_tree.nodes["Principled BSDF"].inputs[27].default_value = 5.0
        yildiz.data.materials.append(mat_y)

        # Yıldız parıldama animasyonu
        yildiz.scale = (1, 1, 1)
        yildiz.keyframe_insert(data_path="scale", frame=1)
        parlak = 1 + random.uniform(0.3, 0.8)
        yildiz.scale = (parlak, parlak, parlak)
        yildiz.keyframe_insert(data_path="scale", frame=random.randint(15, 30))
        yildiz.scale = (1, 1, 1)
        yildiz.keyframe_insert(data_path="scale", frame=random.randint(31, 60))

    # Bulutlar (basit elipsoidler)
    for i, (x, y, z) in enumerate([(-4, 0, 1), (0, 0, 2), (5, 0, 0.5)]):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, y, z))
        bulut = bpy.context.active_object
        bulut.scale = (2, 1, 0.8)
        mat_b = bpy.data.materials.new(f"BulutMat_{{i}}")
        mat_b.use_nodes = True
        mat_b.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.9, 1.0, 1)
        mat_b.node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0.1
        bulut.data.materials.append(mat_b)

        # Bulut yüzme animasyonu
        bulut.location = (x, y, z)
        bulut.keyframe_insert(data_path="location", frame=1)
        bulut.location = (x + 0.5, y, z)
        bulut.keyframe_insert(data_path="location", frame=90)
        bulut.location = (x, y, z)
        bulut.keyframe_insert(data_path="location", frame=180)

    # Ay sallanma animasyonu
    ay.location = (3, 0, 3)
    ay.keyframe_insert(data_path="location", frame=1)
    ay.location = (3, 0, 3.3)
    ay.keyframe_insert(data_path="location", frame=60)
    ay.location = (3, 0, 3)
    ay.keyframe_insert(data_path="location", frame=120)

    # Işık
    bpy.ops.object.light_add(type='POINT', location=(3, -5, 5))
    isik = bpy.context.active_object
    isik.data.energy = 500
    isik.data.color = (1.0, 0.9, 0.7)

def sahne_neseli():
    """Renkli, neşeli gün sahnesi"""
    # Açık mavi gökyüzü
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.4, 0.7, 1.0, 1)

    # Güneş
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(4, 0, 4))
    gunes = bpy.context.active_object
    mat_g = bpy.data.materials.new("GunesMat")
    mat_g.use_nodes = True
    mat_g.node_tree.nodes["Principled BSDF"].inputs[26].default_value = (1.0, 0.9, 0.0, 1)
    mat_g.node_tree.nodes["Principled BSDF"].inputs[27].default_value = 5.0
    gunes.data.materials.append(mat_g)

    # Dönen animasyon
    gunes.rotation_euler = (0, 0, 0)
    gunes.keyframe_insert(data_path="rotation_euler", frame=1)
    gunes.rotation_euler = (0, 0, 6.28)
    gunes.keyframe_insert(data_path="rotation_euler", frame=120)

    # Renkli toplar (zıplama animasyonu)
    renkler = [(1,0,0,1), (0,1,0,1), (0,0,1,1), (1,1,0,1), (1,0,1,1)]
    for i, renk in enumerate(renkler):
        x = (i - 2) * 2
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(x, 0, 0))
        top = bpy.context.active_object
        mat_t = bpy.data.materials.new(f"TopMat_{{i}}")
        mat_t.use_nodes = True
        mat_t.node_tree.nodes["Principled BSDF"].inputs[0].default_value = renk
        top.data.materials.append(mat_t)

        # Zıplama animasyonu
        gecikme = i * 6
        top.location = (x, 0, 0)
        top.keyframe_insert(data_path="location", frame=1 + gecikme)
        top.location = (x, 0, 2)
        top.keyframe_insert(data_path="location", frame=15 + gecikme)
        top.location = (x, 0, 0)
        top.keyframe_insert(data_path="location", frame=30 + gecikme)

    # Işık
    bpy.ops.object.light_add(type='SUN', location=(0, -5, 10))
    isik = bpy.context.active_object
    isik.data.energy = 3

# Sahneye göre oluştur
sahne_turu = "{sahne_turu}"
if sahne_turu == "ninni":
    sahne_ninni()
else:
    sahne_neseli()

# Render et
print("Render başlıyor...")
bpy.ops.render.render(animation=True)
print("Render tamamlandı!")
'''
    return script

def blender_render_et(sahne_turu, sure_saniye, cikti_dosyasi):
    """Blender ile render işlemini başlat"""
    import tempfile
    import subprocess

    # Script dosyasını geçici olarak kaydet
    script_icerik = blender_scriptini_olustur(sahne_turu, sure_saniye, cikti_dosyasi)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_icerik)
        script_yolu = f.name

    try:
        print(f"Blender render başlıyor: {sahne_turu}, {sure_saniye}s")
        komut = [
            "blender", "--background",
            "--python", script_yolu
        ]
        result = subprocess.run(komut, capture_output=False, text=True)
        if result.returncode != 0:
            raise RuntimeError("Blender render hatası")
        print(f"Render tamamlandı: {cikti_dosyasi}")
    finally:
        os.unlink(script_yolu)

    return cikti_dosyasi


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sahne", default="ninni", choices=["ninni", "neseli"])
    parser.add_argument("--sure", type=int, default=10)
    parser.add_argument("--cikti", default="animasyonlar/test_animasyon.mp4")
    args = parser.parse_args()

    blender_render_et(args.sahne, args.sure, args.cikti)
