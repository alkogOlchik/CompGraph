Shader "Custom/Water"
{
    Properties
    {
        [Header(Main)]
        _Color ("Color", Color) = (1,1,1,1)
        _Glossiness("Smoothness", Range(0,1)) = 0.5
        _Metallic("Metallic", Range(0,1)) = 0.0
	
	[Header(Algae)]
    	_AlgaeTex("Algae Texture", 2D) = "white" {}
    	_AlgaeIntensity("Algae Intensity", Range(0, 1)) = 0.5

	 _AlgaeSmoothness("Algae Smoothness", Range(0, 1)) = 0.5 // Гладкость тины
        _AlgaeMetallic("Algae Metallic", Range(0, 1)) = 0.0      // Металличность тины

	
        [Header(Waves)]
        _WaveA("Wave A (dir, steepness, wavelength)", Vector) = (1, 0, 0.5, 10)
        _WaveB("Wave B (dir, steepness, wavelength)", Vector) = (0, 1, 0.25, 20)
        _WaveC("Wave C (dir, steepness, wavelength)", Vector) = (1, 1, 0.15, 10)
        _WaveD("Wave D (dir, steepness, wavelength)", Vector) = (1, 1, 0.5, 10)

        [Header(Fog)]
        _WaterFogColor("Water Fog Color", Color) = (0, 0, 0, 0)
        _WaterFogDensity("Water Fog Density", Range(0, 10)) = 0.1
	_WaterFogSmoothness("Water Fog Smoothness", Range(0,1)) =0.5
        [Header(Reflection)]
        _CubeMap("Cube Map", CUBE) = "white" {}
        _ReflectionStrength("Reflection Strength", Range(0, 1)) = 1

        [Header(Refraction)]
        _RefractionStrength("Refraction Strength", Range(0, 1)) = 0.25
        _RefractionStrength2("Refraction Strength2", Range(0, 1)) = 0.25

        [Header(Distortion)]
        _MainTex("Albedo (RGB)", 2D) = "white" {}
        [NoScaleOffset] _FlowMap("RG Flow, B speed, A noise)", 2D) = "black" {}
        [NoScaleOffset] _DerivHeightMap("AG Derivatives, B Height ", 2D) = "black" {}
        _UJump("U jump per phase", Range(-0.25, 0.25)) = 0.25
        _VJump("V jump per phase", Range(-0.25, 0.25)) = 0.25
        _Tiling("Tiling", Float) = 1
        _Speed("Speed", Float) = 1
        _FlowStrength("Flow Strength", Float) = 1
        _FlowOffset("Flow Offset", Float) = 0
        _HeightScale("Constant Height Scale", Float) = 0.25
        _HeightScaleModulated("Modulated Height Scale", Float) = 0.75
	_Smoothness("Smoothness", Range(0,1)) =0.5
    }
        SubShader
        {
            Tags { "RenderType" = "Transparent" "Queue" = "Transparent"}
            LOD 200
            CULL OFF
            GrabPass { "_WaterBackground" }
            CGPROGRAM
            #pragma surface surf Standard alpha finalcolor:ResetAlphaAtEnd vertex:vert addshadow

            #pragma target 3.0
            #include "Flow.cginc"

            #include "LookingThroughWater.cginc"

            samplerCUBE _CubeMap;
            sampler2D _MainTex, _FlowMap, _DerivHeightMap;
		    sampler2D _AlgaeTex; // Текстура тины
            float _AlgaeIntensity; // Интенсивность тины

            float _UJump, _VJump, _Tiling, _Speed, _FlowStrength, _FlowOffset, _HeightScale, _HeightScaleModulated;
            float _ReflectionStrength;
            float4 _WaveA, _WaveB, _WaveC, _WaveD;

            struct Input
            {
                float2 uv_MainTex;
                float4 screenPos;
                float3 viewDir;
                float3 worldRefl;
                INTERNAL_DATA
            };

            half _Glossiness;
            half _Metallic;
            fixed4 _Color;
		

            float3 GerstnerWave(float4 wave, float3 p, inout float3 tangent, inout float3 binormal) {
                float wavelength = wave.w;
                float k = 2 * UNITY_PI / wavelength;
                float steepness = wave.z;
                float amplitude = steepness / k * 0.001;
                float c = sqrt(9.8 / k);

                float2 dir = normalize(wave.xy);
                float function = k * (dot(dir, p.xz) - c * _Time.y*0.3);

                tangent += 0.005*float3(
                    dir.x * dir.x * (steepness * sin(function)),
                    dir.x * (steepness * cos(function)),
                    -dir.x * dir.y * (steepness * sin(function)));
                binormal += 2*float3(
                    -dir.x * dir.y * (steepness * sin(function)),
                    dir.y * (steepness * cos(function)),
                    -dir.y * dir.y * (steepness * sin(function)));

                return float3(
                    dir.x * (amplitude * cos(function)),
                    amplitude * sin(function),
                    dir.y * (amplitude * cos(function)));
            }

            void ResetAlphaAtEnd(Input IN, SurfaceOutputStandard o, inout fixed4 color) {
                color.a = 1;
            }

            float3 ScaleAndUnpackDerivative(float4 textureData) {
                float3 dh = textureData.agb;
                dh.xy = dh.xy * 2 - 1;
                return dh;
            }
            void vert(inout appdata_full vertexData) {
                float3 p = vertexData.vertex.xyz;
                float3 tangent = float3(1, 0, 0);
                float3 binormal = float3(0, 0, 1);
                p += GerstnerWave(_WaveA, vertexData.vertex.xyz, tangent, binormal);
                p += GerstnerWave(_WaveB, vertexData.vertex.xyz, tangent, binormal);
                p += GerstnerWave(_WaveC, vertexData.vertex.xyz, tangent, binormal);
                p += GerstnerWave(_WaveD, vertexData.vertex.xyz, tangent, binormal);

                float3 normal = normalize(cross(binormal, tangent));
                
                vertexData.vertex.xyz = p;
                vertexData.normal = normal;
            }

            void surf (Input IN, inout SurfaceOutputStandard o)
            {
                float3 flow = tex2D(_FlowMap, IN.uv_MainTex).rgb;
                flow.xy = flow.xy * 2 - 1;
                flow *= _FlowStrength;
                float noise = tex2D(_FlowMap, IN.uv_MainTex).a;
                float time = _Time.y * _Speed *0.2 + noise;
                float2 jump = float2(_UJump, _VJump);

                float3 uvwA = FlowUVW(IN.uv_MainTex, flow.xy, jump, _FlowOffset, _Tiling, time, false);
                float3 uvwB = FlowUVW(IN.uv_MainTex, flow.xy, jump, _FlowOffset, _Tiling, time, true);


                float height = length(flow.z) * _HeightScaleModulated + _HeightScale;


                float3 dhA = ScaleAndUnpackDerivative(tex2D(_DerivHeightMap, uvwA.xy)) * (uvwA.z * height);
                float3 dhB = ScaleAndUnpackDerivative(tex2D(_DerivHeightMap, uvwB.xy)) * (uvwB.z * height);
                o.Normal = normalize(float3(-(dhA.xy + dhB.xy), 1));

                fixed4 textureA = tex2D(_MainTex, uvwA.xy) * uvwA.z;
                fixed4 textureB = tex2D(_MainTex, uvwB.xy) * uvwB.z;
                fixed4 color = (textureA + textureB) * _Color;
                o.Albedo = color.rgb;
		
		float3 algaeTexColor = tex2D(_AlgaeTex, IN.uv_MainTex * _Tiling).rgb;

    float algaeMask = smoothstep(0.0, 0.3, dhA.b + dhB.b); // Маска для высоты волн
    algaeMask *= _AlgaeIntensity; // Регулировка интенсивности


    o.Albedo = lerp(o.Albedo, algaeTexColor, algaeMask);
		
                o.Metallic = _Metallic;
                o.Smoothness = _Glossiness;
                o.Alpha = color.a;
                o.Emission = ColorBelowWater(IN.screenPos, o.Normal * 20) * (1 - color.a)
                    + texCUBE(_CubeMap, WorldReflectionVector(IN, o.Normal)).rgb * (1 - dot(IN.viewDir, o.Normal)) * (1 - _ReflectionStrength);
            }
            ENDCG
    }
    FallBack "Diffuse"
}
