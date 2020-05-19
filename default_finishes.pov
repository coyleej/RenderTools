#version 3.7;
global_settings { assumed_gamma 1.0 }

/*  Render with
povray default_finishes.pov +A +WT1 && eog default_finishes.png

Includes the filter and transmit overrides present for the
irid, translucent, glass, and SiO2 finishes
Also added an example coating with IOR=1.8, f=0.9, and t=0.1

Text labels clearly identify the sphere finish.
*/

#declare SpacingX = 6;
#declare SpacingY = 10;
#declare Radius = 2.25;
#declare TextOffsetX = 0;
#declare TextOffsetY = 1.40*Radius;
#declare TextOffsetZ = Radius;
#declare TextColor = color rgb <0.0, 0.0, 0.0>;
#declare TextFinish = finish { ambient 0.9 diffuse 0.6 };

camera
    {
    orthographic
    angle 94
    location <0.5, 0, -15>
    look_at <0.5, 0, 0>
    }

light_source
    {
    <-400, 400, -600>
    color rgb <1, 1, 1>
    }

// Checkered background
plane 
    {
    z, 1.01 * Radius 
    texture { pigment { checker color rgb 0.55 color rgb 1 } }
    }

// dull
#declare DullSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0, 0> }
        }
    text
        {
        ttf "cyrvetic.ttf" "dull" 1, 0
        translate <-0.9+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// billiard
#declare BilliardSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0, 0> }
        finish
            {
            ambient 0.3
            diffuse 0.8
            specular 0.2
            roughness 0.005
            metallic 0.5
            }
        }
    text
        {
        ttf "cyrvetic.ttf" "billiard" 1, 0
        translate <-1.35+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// irid
#declare IridSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0.7, 0> }
        finish
            {
            phong 0.5
            reflection { 0.2 metallic }
            diffuse 0.3
            irid { 0.75 thickness 0.5 turbulence 0.5 }
            }
        interior { ior 1.5 }
        }
    text
        {
        ttf "cyrvetic.ttf" "irid" 1, 0
        translate <-0.5+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// translucent
#declare TranslucentSphere = union {
    sphere
        {
        <0, 0, 0>, Radius
        pigment {color rgbft <1, 0, 0, 0.667, 0.02> }
        finish
            {
            emission 0.10
            diffuse 0.85
            specular 0.4
            brilliance 4
            reflection { 0.5 fresnel on }
            }
        interior { ior 1.0 }
        }
    text
        {
        ttf "cyrvetic.ttf" "translucent" 1, 0
        translate <-2.4+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// coating with IOR 1.8, custom transparency
#declare CoatingSphere = union {
    sphere
        {
        <0, 0, 0>, Radius
        pigment {color rgbft <1, 0, 0, 0.9, 0.1> }
        finish
            {
            emission 0.10
            diffuse 0.85
            specular 0.4
            brilliance 4
            reflection { 0.5 fresnel on }
            }
        interior { ior 1.8 }
        }
    text
        {
        ttf "cyrvetic.ttf" "example" 1, 0
        translate <-1.8+TextOffsetX, 1+TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    text
        {
        ttf "cyrvetic.ttf" "coating" 1, 0
        translate <-1.6+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// glass
#declare GlassSphere = union {
    sphere
        {
        <0, 0, 0>, Radius
        pigment {color rgbft <1, 0, 0, 0.95, 0> }
        finish
            {
            phong 0.8
            phong_size 100
            brilliance 5
            reflection { 0.2, 1.0 fresnel on }
            }
        interior { ior 1.5 }
        }
    text
        {
        ttf "cyrvetic.ttf" "glass" 1, 0
        translate <-1.15+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// SiO2
#declare SiO2Sphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0.98, 0> }
        finish 
            {
            specular 0.6
            brilliance 5
            roughness 0.001
            reflection { 0.0, 1.0 fresnel on }
            }
        interior { ior 1.45 }
        }
    text
        {
        ttf "cyrvetic.ttf" "SiO2" 1, 0
        translate <-1+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// dull_metal
#declare DullMetalSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0, 0> }
        finish
            {
            emission 0.1
            diffuse 0.1
            specular 1.0
            roughness 0.001
            reflection 0.5 metallic
            metallic
            }
        }
    text
        {
        ttf "cyrvetic.ttf" "dull_metal" 1, 0
        translate <-2.2+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// bright_metal
#declare BrightMetalSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0, 0> }
        finish
            {
            emission 0.2
            diffuse 0.3
            specular 0.8
            roughness 0.01
            reflection 0.5 metallic
            metallic
            }
        }
    text
        {
        ttf "cyrvetic.ttf" "bright_metal" 1, 0
        translate <-2.7+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

// silicon
#declare SiliconSphere = union {
    sphere
        {
        <0, 0, 0> Radius
        pigment {color rgbft <1, 0, 0, 0, 0> }
        finish 
            {
            diffuse 0.2
            brilliance 5
            phong 1
            phong_size 250
            roughness 0.01
            reflection <0.10, 0.10, 0.5> metallic
            metallic
            }
        // IOR taken from blender
        interior { ior 4.24 }
        }
    text
        {
        ttf "cyrvetic.ttf" "silicon" 1, 0
        translate <-1.3+TextOffsetX, TextOffsetY, TextOffsetZ>
        pigment { TextColor }
        finish { TextFinish }
        no_shadow
        }
    }

object { 
    DullSphere 
    translate <-2*SpacingX, -0.5*SpacingY, 0>
    }
object { 
    BilliardSphere 
    translate <-SpacingX, -0.5*SpacingY, 0>
    }
object { 
    IridSphere 
    translate <0, 0.5*SpacingY, 0>
    }
object { 
    TranslucentSphere 
    translate <SpacingX, 0.5*SpacingY, 0>
    }
object { 
    CoatingSphere 
    translate <2*SpacingX, 0.5*SpacingY, 0>
    }
object { 
    GlassSphere 
    translate <-2*SpacingX, 0.5*SpacingY, 0>
    }
object { 
    SiO2Sphere 
    translate <-SpacingX, 0.5*SpacingY, 0>
    }
object { 
    DullMetalSphere 
    translate <0, -0.5*SpacingY, 0>
    }
object { 
    BrightMetalSphere 
    translate <SpacingX, -0.5*SpacingY, 0>
    }
object { 
    SiliconSphere 
    translate <2*SpacingX, -0.5*SpacingY, 0>
    }

