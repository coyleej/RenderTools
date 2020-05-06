#version 3.7;
global_settings { assumed_gamma 1.0 }

/*  Render with
povray default_finishes.pov +ua +A +WT1 && eog default_finishes.png

Includes the filter and transmit overrides present for the
irid, translucent, glass, and SiO2 finishes
Also added an example coating with IOR=1.8, f=0.9, and t=0.1

Organization in output image:
Top row (l->r): dull, billiard, irid
Middle row (l->r): translucent, example coating, glass, SiO2
Bottom row (l->r): dull_metal, bright_metal, silicon
*/

camera
    {
    orthographic
    angle 70
    location <15, 0, 0>
    look_at <0, 0, 0>
    sky <0, 0, 1>
    }

light_source
    {
    <10, 15, 18>
    color rgb <1, 1, 1>
    }

background { rgb <1, 1, 1> }

#declare Spacing = 5;
#declare Radius = 2;

// dull
sphere
    {
    <0, 0, 0> Radius
    pigment {color rgbft <1, 0, 0, 0, 0> }
    translate <0, Spacing, Spacing>
    }

// billiard
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
    translate <0, 0, Spacing>
    }

// irid
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
    translate <0, -Spacing, Spacing>
    }

// translucent
sphere
    {
    <0, 0, 0>, Radius
    pigment {color rgbft <1, 0, 0, 0.667, 0.02> }
    finish
        {
        emission 0.25
        diffuse 0.75
        specular 0.4
        brilliance 4
        reflection { 0.5 fresnel on }
        }
    interior { ior 1.0 }
    translate <0, 1.5*Spacing, 0>
    }

// coating with IOR 1.8, custom transparency
sphere
    {
    <0, 0, 0>, Radius
    pigment {color rgbft <1, 0, 0, 0.9, 0.1> }
    finish
        {
        emission 0.25
        diffuse 0.75
        specular 0.4
        brilliance 4
        reflection { 0.5 fresnel on }
        }
    interior { ior 1.8 }
    translate <0, 0.5*Spacing, 0>
    }

// glass
sphere
    {
    <0, 0, 0>, Radius
    pigment {color rgbft <1, 0, 0, 0.95, 0> }
    finish
        {
        specular 0.6
        phong 0.8
        brilliance 5
        reflection { 0.2, 1.0 fresnel on }
        }
    interior { ior 1.5 }
    translate <0, -0.5*Spacing, 0>
    }

// SiO2
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
    translate <0, -1.5*Spacing, 0>
    }

// dull_metal
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
    translate <0, Spacing, -Spacing>
    }

// bright_metal
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
    translate <0, 0, -Spacing>    }

// silicon
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
    translate <0, -Spacing, -Spacing>
    }

