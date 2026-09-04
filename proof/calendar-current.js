(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.98e6a0d0b56afd13.js","sha256":"98e6a0d0b56afd135b23190fc66684f7e6a9e0a501e186e65e9371ad4b077bbd","count":2539,"publishedAt":"2026-09-04T11:34:41Z","state":"calendar-state.json","stateSha256":"21f6333083123f5a1b3a4a2d705117c0d48fbb1832e9f246e6a5842717be8be0"});
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
