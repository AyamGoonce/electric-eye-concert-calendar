(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3823b29ef628d5d8.js","sha256":"3823b29ef628d5d8ddbe4bb1675c91f6eae576bd86a7442d39365014a188a5c7","count":2098,"publishedAt":"2026-10-17T23:13:06Z","state":"calendar-state.json","stateSha256":"34490414bf006f5576e54d6a4c4d183ae47c158cf417629b8956de4c36be08d4","sourceState":"calendar-source-state.json","sourceStateSha256":"6bc54411908e2647595715588edcffec0c6b645b225cb00d707b64f5cb783afd"});
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
