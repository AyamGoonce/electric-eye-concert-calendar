(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5bee87fa07945938.js","sha256":"5bee87fa079459383750c1e1e21928393b0481b4268e57d30ae48e545ba32eea","count":2062,"publishedAt":"2026-10-20T08:41:29Z","state":"calendar-state.json","stateSha256":"687532cf04a749ebd2760a1149f3eec4f40ceb6bcecdb1403577db4c7782c903","sourceState":"calendar-source-state.json","sourceStateSha256":"0926947c6d4e3ad8843ca2a54b0b5f86e785a3235ec67bee330899dc09b96eb3"});
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
