(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c40ea103bcd448aa.js","sha256":"c40ea103bcd448aa4c08c7b48ea7e82be2b2a40a1ffa4aeb0811b0c0bcb8bc0f","count":2182,"publishedAt":"2026-10-04T10:21:21Z","state":"calendar-state.json","stateSha256":"fa61df841c45f15b8bfb4d12b7a37469f9542017f59f0696c90cb633d3ea765d","sourceState":"calendar-source-state.json","sourceStateSha256":"02a0853951ad57d5f46e5f9da2f3d2d84e7a7cfcf0e1df603528f6f926c0e6f2"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
