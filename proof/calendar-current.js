(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aa3c8e8ad622783e.js","sha256":"aa3c8e8ad622783e271f87e1850ca8f41ab0d16c70463a5da15904b6a55fa80a","count":2115,"publishedAt":"2026-11-18T11:52:03Z","state":"calendar-state.json","stateSha256":"79085e5c528b65472ad439a38c583b0dc0931666f423e247895e2a2993d8eeb2","sourceState":"calendar-source-state.json","sourceStateSha256":"1b735b07bf2150b436de6758721b0afa1c6c216546972370f351b27cc6e67607"});
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
