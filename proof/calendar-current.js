(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4cd8cdf38dcbec26.js","sha256":"4cd8cdf38dcbec26dc0af97e34a3ab4895b80750ac65c94ba0a9f51f28ae80d7","count":2115,"publishedAt":"2026-11-18T11:20:57Z","state":"calendar-state.json","stateSha256":"3b4d3d7e84dfb03e69470aff67f1ae1892a883083b7fc9e0ae500095fa4b38f0","sourceState":"calendar-source-state.json","sourceStateSha256":"b70aed465b2000317071ae1321f25940edadef6d666049ee822a5f9f9875ca22"});
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
